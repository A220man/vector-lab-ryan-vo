from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import hashlib
import json

from app.core.database import get_session
from app.models import Document, DocumentStatus, IndexNode, DocumentVersion
from app.services.indexing import build_index, incremental_update_index

router = APIRouter(prefix="", tags=["documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    content = await file.read()
    content_hash = hashlib.sha256(content).hexdigest()

    # Check if document with this hash already exists
    existing = await session.execute(
        select(Document).where(Document.content_hash == content_hash)
    )
    existing_doc = existing.scalar_one_or_none()
    if existing_doc:
        return {
            "id": existing_doc.id,
            "filename": existing_doc.filename,
            "status": existing_doc.status.value,
            "content_hash": existing_doc.content_hash,
            "message": "Document already exists",
        }

    doc = Document(
        filename=file.filename,
        content_hash=content_hash,
        status=DocumentStatus.PENDING,
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)

    return {
        "id": doc.id,
        "filename": doc.filename,
        "status": doc.status.value,
        "content_hash": doc.content_hash,
    }


@router.get("")
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit)
    )
    docs = result.scalars().all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "status": d.status.value,
            "page_count": d.page_count,
            "version": d.version,
            "content_hash": d.content_hash,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in docs
    ]


@router.get("/{doc_id}")
async def get_document(
    doc_id: int,
    session: AsyncSession = Depends(get_session),
):
    doc = await session.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": doc.id,
        "filename": doc.filename,
        "status": doc.status.value,
        "page_count": doc.page_count,
        "version": doc.version,
        "content_hash": doc.content_hash,
        "parent_id": doc.parent_id,
        "error_message": doc.error_message,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
        "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
    }


@router.post("/{doc_id}/index")
async def index_document(
    doc_id: int,
    session: AsyncSession = Depends(get_session),
):
    doc = await session.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.status = DocumentStatus.PROCESSING
    await session.commit()

    try:
        # For now, use mock content - real implementation would extract from PDF
        mock_pages = [
            {"page_num": 1, "text": "Chapter 1: Introduction\nThis is the first chapter."},
            {"page_num": 2, "text": "Section 1.1: Background\nBackground information here."},
            {"page_num": 3, "text": "Section 1.2: Motivation\nMotivation for this work."},
            {"page_num": 4, "text": "Chapter 2: Methods\nThis chapter describes methods."},
            {"page_num": 5, "text": "Section 2.1: Algorithm\nAlgorithm details here."},
        ]
        await build_index(doc, mock_pages, session)
        doc.status = DocumentStatus.INDEXED
        await session.commit()
        return {"message": "Indexing complete", "document_id": doc_id}
    except Exception as e:
        doc.status = DocumentStatus.FAILED
        doc.error_message = str(e)
        await session.commit()
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}")


@router.post("/{doc_id}/incremental-update")
async def incremental_update_document(
    doc_id: int,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    """Update document incrementally - only rebuild changed sections."""
    doc = await session.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    new_content = await file.read()
    new_hash = hashlib.sha256(new_content).hexdigest()

    if new_hash == doc.content_hash:
        return {"message": "No changes detected", "document_id": doc_id}

    # Create new version record
    old_version = doc.version
    doc.version += 1
    doc.content_hash = new_hash
    doc.status = DocumentStatus.PROCESSING

    version_record = DocumentVersion(
        document_id=doc.id,
        version=old_version,
        content_hash=doc.content_hash,
        change_summary="Incremental update",
    )
    session.add(version_record)
    await session.commit()

    try:
        # Mock new pages for demo
        mock_pages = [
            {"page_num": 1, "text": "Chapter 1: Introduction\nThis is the first chapter."},
            {"page_num": 2, "text": "Section 1.1: Background\nUpdated background information."},
            {"page_num": 3, "text": "Section 1.2: Motivation\nMotivation for this work."},
            {"page_num": 4, "text": "Chapter 2: Methods\nThis chapter describes methods."},
            {"page_num": 5, "text": "Section 2.1: Algorithm\nImproved algorithm details."},
        ]
        changed_nodes = await incremental_update_index(doc, mock_pages, session)
        doc.status = DocumentStatus.INDEXED
        version_record.changed_node_ids = json.dumps(changed_nodes)
        await session.commit()
        return {
            "message": "Incremental update complete",
            "document_id": doc_id,
            "changed_nodes": changed_nodes,
        }
    except Exception as e:
        doc.status = DocumentStatus.FAILED
        doc.error_message = str(e)
        await session.commit()
        raise HTTPException(status_code=500, detail=f"Incremental update failed: {e}")


@router.get("/{doc_id}/versions")
async def get_document_versions(
    doc_id: int,
    session: AsyncSession = Depends(get_session),
):
    doc = await session.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    result = await session.execute(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == doc_id)
        .order_by(DocumentVersion.version.desc())
    )
    versions = result.scalars().all()
    return [
        {
            "version": v.version,
            "content_hash": v.content_hash,
            "changed_node_ids": json.loads(v.changed_node_ids) if v.changed_node_ids else [],
            "change_summary": v.change_summary,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }
        for v in versions
    ]
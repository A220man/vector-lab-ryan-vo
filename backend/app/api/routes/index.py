from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import json

from app.core.database import get_session
from app.models import Document, IndexNode
from app.services.indexing import get_tree_structure, get_leaf_nodes, search_nodes

router = APIRouter(prefix="", tags=["index"])


@router.get("/{doc_id}/tree")
async def get_index_tree(
    doc_id: int,
    session: AsyncSession = Depends(get_session),
):
    doc = await session.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    tree = await get_tree_structure(doc_id, session)
    return {"document_id": doc_id, "tree": tree}


@router.get("/{doc_id}/leaves")
async def get_index_leaves(
    doc_id: int,
    session: AsyncSession = Depends(get_session),
):
    doc = await session.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    leaves = await get_leaf_nodes(doc_id, session)
    return {"document_id": doc_id, "leaves": leaves}


@router.get("/{doc_id}/search")
async def search_index(
    doc_id: int,
    q: str,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
):
    doc = await session.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    results = await search_nodes(doc_id, q, limit, session)
    return {"document_id": doc_id, "query": q, "results": results}


@router.get("/{doc_id}/nodes/{node_id}")
async def get_node_detail(
    doc_id: int,
    node_id: str,
    session: AsyncSession = Depends(get_session),
):
    doc = await session.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    result = await session.execute(
        select(IndexNode).where(
            IndexNode.document_id == doc_id,
            IndexNode.node_id == node_id,
        )
    )
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    return {
        "node_id": node.node_id,
        "structure": node.structure,
        "title": node.title,
        "content": node.content,
        "summary": node.summary,
        "level": node.level,
        "parent_node_id": node.parent_node_id,
        "start_page": node.start_page,
        "end_page": node.end_page,
        "content_hash": node.content_hash,
        "summary_hash": node.summary_hash,
    }
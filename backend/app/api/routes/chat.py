from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_session
from app.models import Document, ChatSession, ChatMessage, IndexNode
from app.services.chat import chat_completion

router = APIRouter(prefix="", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    document_id: Optional[int] = None
    session_id: Optional[int] = None
    model: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: int
    usage: dict


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session: AsyncSession = Depends(get_session),
):
    if request.document_id:
        doc = await session.get(Document, request.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

    # Get or create session
    if request.session_id:
        chat_session = await session.get(ChatSession, request.session_id)
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        chat_session = ChatSession(
            document_id=request.document_id,
            title=request.message[:50] if request.message else "New Chat",
        )
        session.add(chat_session)
        await session.commit()
        await session.refresh(chat_session)

    # Save user message
    user_msg = ChatMessage(
        session_id=chat_session.id,
        role="user",
        content=request.message,
    )
    session.add(user_msg)

    # Get relevant context from document if available
    context = ""
    if request.document_id:
        # Simple context retrieval - in production would use vector search
        result = await session.execute(
            select(IndexNode)
            .where(IndexNode.document_id == request.document_id)
            .limit(5)
        )
        nodes = result.scalars().all()
        context = "\n\n".join([f"{n.title}: {n.content or n.summary or ''}" for n in nodes])

    # Call LLM with error handling to preserve usage on failure
    response_text = ""
    usage = {
        "model": request.model or "unknown",
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "reasoning_tokens": 0,
        "complete": -1,  # -1 = unknown (failure/cancellation)
    }
    try:
        response_text, usage = await chat_completion(
            message=request.message,
            context=context,
            model=request.model,
        )
        # Ensure usage has complete flag
        usage.setdefault("complete", 1)
    except Exception as e:
        # Preserve partial usage if available, mark as failed
        response_text = f"Error: {str(e)}"
        usage["complete"] = -1

    # Save assistant message with usage (even on failure)
    assistant_msg = ChatMessage(
        session_id=chat_session.id,
        role="assistant",
        content=response_text,
        model=usage.get("model"),
        usage_input_tokens=usage.get("input_tokens"),
        usage_output_tokens=usage.get("output_tokens"),
        usage_cache_read_tokens=usage.get("cache_read_tokens"),
        usage_cache_write_tokens=usage.get("cache_write_tokens"),
        usage_reasoning_tokens=usage.get("reasoning_tokens"),
        usage_complete=usage.get("complete", -1),
    )
    session.add(assistant_msg)
    await session.flush()  # Flush to get server-generated created_at

    chat_session.updated_at = assistant_msg.created_at
    await session.commit()

    return ChatResponse(
        response=response_text,
        session_id=chat_session.id,
        usage=usage,
    )


@router.get("/sessions")
async def list_sessions(
    document_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    query = select(ChatSession).order_by(ChatSession.updated_at.desc())
    if document_id:
        query = query.where(ChatSession.document_id == document_id)
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    sessions = result.scalars().all()
    return [
        {
            "id": s.id,
            "document_id": s.document_id,
            "title": s.title,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        }
        for s in sessions
    ]


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: int,
    session: AsyncSession = Depends(get_session),
):
    chat_session = await session.get(ChatSession, session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = await session.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()

    return {
        "id": chat_session.id,
        "document_id": chat_session.document_id,
        "title": chat_session.title,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "model": m.model,
                "usage": {
                    "input_tokens": m.usage_input_tokens,
                    "output_tokens": m.usage_output_tokens,
                    "cache_read_tokens": m.usage_cache_read_tokens,
                    "cache_write_tokens": m.usage_cache_write_tokens,
                    "reasoning_tokens": m.usage_reasoning_tokens,
                    "complete": m.usage_complete,
                },
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ],
    }
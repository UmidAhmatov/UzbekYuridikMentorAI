from __future__ import annotations

import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.disclaimer import LEGAL_AI_DISCLAIMER
from app.database import get_db_session
from app.models import Chat, Message
from app.schemas.chat import ChatStreamRequest
from app.services.claude_client import ClaudeClientError, ClaudeMessage, get_claude_client
from app.services.legal_kb import LegalSearchResult, build_legal_context, retrieve
from app.services.prompts import build_legal_system_prompt

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/stream")
async def stream_chat(
    payload: ChatStreamRequest,
    db: AsyncSession = Depends(get_db_session),
) -> StreamingResponse:
    chat = await _get_or_create_chat(db, payload)
    user_message = Message(chat_id=chat.id, role="user", content=payload.message)
    db.add(user_message)
    await db.commit()

    legal_results = await retrieve(db, payload.message)
    legal_context = build_legal_context(legal_results)
    system_prompt = build_legal_system_prompt(legal_context, payload.language)
    messages = _to_claude_messages(payload)

    async def event_stream() -> AsyncGenerator[str, None]:
        assistant_text: list[str] = []
        yield _sse(
            "context",
            {
                "chat_id": str(chat.id),
                "sources": [_source_payload(result) for result in legal_results],
            },
        )

        try:
            async for token in get_claude_client().stream_messages(
                system_prompt=system_prompt,
                messages=messages,
            ):
                assistant_text.append(token)
                yield _sse("delta", {"text": token})

            content = "".join(assistant_text).strip()
            if content and LEGAL_AI_DISCLAIMER not in content:
                disclaimer_suffix = f"\n\n{LEGAL_AI_DISCLAIMER}"
                assistant_text.append(disclaimer_suffix)
                content = "".join(assistant_text).strip()
                yield _sse("delta", {"text": disclaimer_suffix})

            if content:
                db.add(
                    Message(
                        chat_id=chat.id,
                        role="assistant",
                        content=content,
                        meta={"legal_sources": [_source_payload(result) for result in legal_results]},
                    )
                )
                await db.commit()

            yield _sse("done", {"chat_id": str(chat.id)})
        except ClaudeClientError as exc:
            await db.rollback()
            yield _sse("error", {"message": str(exc), "chat_id": str(chat.id)})
        except Exception:
            await db.rollback()
            yield _sse(
                "error",
                {
                    "message": "Chat streaming vaqtida kutilmagan xato yuz berdi.",
                    "chat_id": str(chat.id),
                },
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def _get_or_create_chat(db: AsyncSession, payload: ChatStreamRequest) -> Chat:
    if payload.chat_id is not None:
        existing = await db.get(Chat, payload.chat_id)
        if existing is not None:
            return existing

    title = payload.message.strip().replace("\n", " ")[:80] or "Yangi suhbat"
    chat = Chat(title=title)
    db.add(chat)
    await db.flush()
    return chat


def _to_claude_messages(payload: ChatStreamRequest) -> list[ClaudeMessage]:
    messages: list[ClaudeMessage] = [
        {"role": item.role, "content": item.content}
        for item in payload.history[-20:]
    ]
    messages.append({"role": "user", "content": payload.message})
    return messages


def _source_payload(result: LegalSearchResult) -> dict[str, object]:
    return {
        "id": result.id,
        "source_id": result.source_id,
        "source_url": result.source_url,
        "law_title": result.law_title,
        "article_number": result.article_number,
        "heading": result.heading,
        "score": result.score,
    }


def _sse(event: str, data: dict[str, object]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

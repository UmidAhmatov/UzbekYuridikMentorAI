from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.disclaimer import LEGAL_AI_DISCLAIMER
from app.database import get_db_session
from app.schemas.mentor import AdviceResponse, AdviceSourceSchema, RoadmapRequest
from app.services.claude_client import ClaudeClientError, get_claude_client
from app.services.legal_kb import LegalSearchResult, build_legal_context, retrieve
from app.services.prompts import build_roadmap_system_prompt

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.post("/generate", response_model=AdviceResponse)
async def generate_roadmap(
    payload: RoadmapRequest,
    db: AsyncSession = Depends(get_db_session),
) -> AdviceResponse:
    user_prompt = _build_user_prompt(payload)
    legal_results = await retrieve(db, user_prompt)
    system_prompt = build_roadmap_system_prompt(
        language=payload.language,
        legal_context=build_legal_context(legal_results),
    )

    try:
        content = await get_claude_client().complete_message(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except ClaudeClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not content:
        raise HTTPException(status_code=502, detail="Claude yo'l xaritasini qaytarmadi.")

    return AdviceResponse(
        title=_title_for_language(payload.language),
        content=content,
        disclaimer=LEGAL_AI_DISCLAIMER,
        sources=[_source_schema(result) for result in legal_results],
    )


def _build_user_prompt(payload: RoadmapRequest) -> str:
    details = [
        f"Vaziyat: {payload.situation.strip()}",
        f"Maqsad: {payload.goal.strip()}",
    ]
    if payload.region:
        details.append(f"Hudud: {payload.region.strip()}")
    if payload.event_date:
        details.append(f"Muhim sana yoki hodisa sanasi: {payload.event_date.strip()}")
    if payload.available_documents:
        details.append(f"Mavjud hujjatlar: {payload.available_documents.strip()}")
    return "\n".join(details)


def _source_schema(result: LegalSearchResult) -> AdviceSourceSchema:
    return AdviceSourceSchema(
        id=result.id,
        source_url=result.source_url,
        law_title=result.law_title,
        article_number=result.article_number,
        heading=result.heading,
    )


def _title_for_language(language) -> str:
    if language.value == "uz-cyrillic":
        return "Ҳуқуқий йўл харитаси"
    if language.value == "ru":
        return "Правовая дорожная карта"
    return "Huquqiy yo'l xaritasi"


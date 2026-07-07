from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.disclaimer import LEGAL_AI_DISCLAIMER
from app.schemas.mentor import AdviceResponse, CareerRequest
from app.services.claude_client import ClaudeClientError, get_claude_client
from app.services.prompts import build_career_system_prompt

router = APIRouter(prefix="/career", tags=["career"])


@router.post("/advise", response_model=AdviceResponse)
async def advise_career(payload: CareerRequest) -> AdviceResponse:
    try:
        content = await get_claude_client().complete_message(
            system_prompt=build_career_system_prompt(payload.language),
            messages=[{"role": "user", "content": _build_user_prompt(payload)}],
        )
    except ClaudeClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not content:
        raise HTTPException(status_code=502, detail="Claude karyera rejasini qaytarmadi.")

    return AdviceResponse(
        title=_title_for_language(payload.language),
        content=content,
        disclaimer=LEGAL_AI_DISCLAIMER,
    )


def _build_user_prompt(payload: CareerRequest) -> str:
    details = [
        f"Hozirgi rol yoki holat: {payload.current_role.strip()}",
        f"Tajriba darajasi: {payload.experience_level.strip()}",
        f"Maqsadli rol: {payload.target_role.strip()}",
        f"Ko'nikmalar: {payload.skills.strip()}",
    ]
    if payload.region:
        details.append(f"Ish qidiriladigan hudud: {payload.region.strip()}")
    if payload.employment_type:
        details.append(f"Ish shakli: {payload.employment_type.strip()}")
    if payload.notes:
        details.append(f"Qo'shimcha ma'lumot: {payload.notes.strip()}")
    return "\n".join(details)


def _title_for_language(language) -> str:
    if language.value == "uz-cyrillic":
        return "Каръера ҳаракат режаси"
    if language.value == "ru":
        return "Карьерный план действий"
    return "Karyera harakat rejasi"


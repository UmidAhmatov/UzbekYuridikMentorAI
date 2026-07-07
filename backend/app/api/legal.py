from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.models import LegalChunk
from app.schemas.legal import LegalSourceStatusSchema
from app.services.legal_sources import LEGAL_SOURCES

router = APIRouter(prefix="/legal", tags=["legal"])


@router.get("/sources", response_model=list[LegalSourceStatusSchema])
async def list_legal_sources(
    db: AsyncSession = Depends(get_db_session),
) -> list[LegalSourceStatusSchema]:
    rows = await db.execute(
        select(
            LegalChunk.source_id,
            func.count(LegalChunk.id),
            func.count(LegalChunk.embedding),
        ).group_by(LegalChunk.source_id)
    )
    counts = {
        source_id: (int(chunk_count), int(embedding_count))
        for source_id, chunk_count, embedding_count in rows.all()
    }

    return [
        LegalSourceStatusSchema(
            key=source.key,
            title=source.title,
            lex_id=source.lex_id,
            source_id=source.source_id,
            url=source.url,
            category=source.category,
            chunk_count=counts.get(source.source_id, (0, 0))[0],
            embedding_count=counts.get(source.source_id, (0, 0))[1],
        )
        for source in LEGAL_SOURCES
    ]


from __future__ import annotations

from sqlalchemy import select, update

from app.database import AsyncSessionLocal
from app.models import LegalChunk
from app.services.embeddings import get_embedding_service


async def backfill_missing_embeddings(
    *,
    batch_size: int = 16,
    max_chunks: int | None = None,
    source_id: str | None = None,
) -> int:
    completed = 0
    while max_chunks is None or completed < max_chunks:
        current_batch_size = batch_size
        if max_chunks is not None:
            current_batch_size = min(current_batch_size, max_chunks - completed)
        if current_batch_size <= 0:
            break

        async with AsyncSessionLocal() as session:
            stmt = (
                select(LegalChunk.id, LegalChunk.content)
                .where(LegalChunk.embedding.is_(None))
                .order_by(LegalChunk.source_id, LegalChunk.chunk_index)
                .limit(current_batch_size)
            )
            if source_id:
                stmt = stmt.where(LegalChunk.source_id == source_id)
            rows = (await session.execute(stmt)).all()
            if not rows:
                break

            embeddings = await get_embedding_service().embed_texts(
                [content for _chunk_id, content in rows]
            )
            for (chunk_id, _content), embedding in zip(rows, embeddings, strict=True):
                await session.execute(
                    update(LegalChunk)
                    .where(LegalChunk.id == chunk_id)
                    .values(embedding=embedding)
                )
            await session.commit()

        completed += len(rows)

    return completed


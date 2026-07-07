from __future__ import annotations

from dataclasses import dataclass, field
import logging
from typing import Any

from sqlalchemy import case, desc, func, literal, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.legal import LegalChunk
from app.services.embeddings import get_embedding_service
from app.services.legal_sources import LEGAL_SOURCES

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LegalChunkPayload:
    source_id: str
    source_url: str
    law_title: str
    content: str
    chunk_index: int
    article_number: str | None = None
    heading: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LegalSearchResult:
    id: str
    source_id: str
    source_url: str
    law_title: str
    article_number: str | None
    heading: str | None
    content: str
    score: float
    vector_score: float | None = None
    trigram_score: float | None = None


async def upsert_chunks(
    session: AsyncSession,
    chunks: list[LegalChunkPayload],
    *,
    with_embeddings: bool = True,
) -> int:
    if not chunks:
        return 0

    embeddings: list[list[float] | None]
    if with_embeddings:
        embeddings = await get_embedding_service().embed_texts([chunk.content for chunk in chunks])
    else:
        embeddings = [None for _ in chunks]

    values = [
        {
            "source_id": chunk.source_id,
            "source_url": chunk.source_url,
            "law_title": chunk.law_title,
            "article_number": chunk.article_number,
            "heading": chunk.heading,
            "content": chunk.content,
            "chunk_index": chunk.chunk_index,
            "embedding": embedding,
            "metadata": chunk.metadata,
        }
        for chunk, embedding in zip(chunks, embeddings, strict=True)
    ]

    table = LegalChunk.__table__
    stmt = insert(table).values(values)
    update_columns = {
        "source_url": stmt.excluded.source_url,
        "law_title": stmt.excluded.law_title,
        "article_number": stmt.excluded.article_number,
        "heading": stmt.excluded.heading,
        "content": stmt.excluded.content,
        "metadata": stmt.excluded.metadata,
        "updated_at": func.now(),
    }
    if with_embeddings:
        update_columns["embedding"] = stmt.excluded.embedding
    else:
        update_columns["embedding"] = case(
            (
                table.c.content.is_distinct_from(stmt.excluded.content),
                None,
            ),
            else_=table.c.embedding,
        )
    stmt = stmt.on_conflict_do_update(
        constraint="uq_legal_chunks_source_id_chunk_index",
        set_=update_columns,
    )

    await session.execute(stmt)
    return len(chunks)


async def retrieve(
    session: AsyncSession,
    query: str,
    *,
    limit: int = 6,
) -> list[LegalSearchResult]:
    query = query.strip()
    if not query:
        return []

    has_vector_chunks = await session.scalar(
        select(LegalChunk.id)
        .where(LegalChunk.embedding.is_not(None))
        .limit(1)
    )
    if has_vector_chunks is None:
        return await retrieve_text_only(session, query, limit=limit)

    try:
        query_embedding = await get_embedding_service().embed_query(query)
    except Exception:
        logger.exception("Embedding retrieval failed; falling back to trigram search.")
        return await retrieve_text_only(session, query, limit=limit)

    vector_score = (1 - LegalChunk.embedding.cosine_distance(query_embedding)).label("vector_score")
    trigram_score = _trigram_score(query).label("trigram_score")
    score = ((vector_score * 0.75) + (trigram_score * 0.25)).label("score")

    candidate_limit = max(limit * 2, 12)
    stmt = (
        select(LegalChunk, score, vector_score, trigram_score)
        .where(LegalChunk.embedding.is_not(None))
        .order_by(desc(score))
        .limit(candidate_limit)
    )
    result = await session.execute(stmt)
    rows = result.all()

    vector_results = [
        _to_search_result(
            chunk=row[0],
            score=float(row[1] or 0),
            vector_score=float(row[2] or 0),
            trigram_score=float(row[3] or 0),
        )
        for row in rows
    ]
    text_results = await retrieve_text_only(session, query, limit=candidate_limit)
    return _reciprocal_rank_fusion(vector_results, text_results, limit=limit)


async def retrieve_text_only(
    session: AsyncSession,
    query: str,
    *,
    limit: int = 6,
) -> list[LegalSearchResult]:
    query = query.strip()
    if not query:
        return []

    trigram_score = _trigram_score(query).label("trigram_score")
    stmt = (
        select(LegalChunk, trigram_score)
        .order_by(desc(trigram_score))
        .limit(limit)
    )
    result = await session.execute(stmt)

    return [
        _to_search_result(
            chunk=row[0],
            score=float(row[1] or 0),
            trigram_score=float(row[1] or 0),
        )
        for row in result.all()
    ]


def build_legal_context(results: list[LegalSearchResult]) -> str:
    blocks = []
    for index, result in enumerate(results, start=1):
        article = f", modda: {result.article_number}" if result.article_number else ""
        heading = f"\nSarlavha: {result.heading}" if result.heading else ""
        blocks.append(
            f"[{index}] Manba: {result.law_title}{article}\n"
            f"URL: {result.source_url}{heading}\n"
            f"Matn: {result.content}"
        )

    return "\n\n".join(blocks)


def _trigram_score(query: str):
    base_score = func.greatest(
        func.similarity(LegalChunk.content, query),
        func.similarity(LegalChunk.law_title, query),
        func.coalesce(func.similarity(LegalChunk.heading, query), 0),
    )
    return base_score + _catalog_title_boost(query)


def _catalog_title_boost(query: str):
    normalized_query = query.casefold()
    matched_source_ids = [
        source.source_id
        for source in LEGAL_SOURCES
        if any(term.casefold() in normalized_query for term in source.search_terms)
    ]
    if not matched_source_ids:
        return literal(0.0)
    return case(
        (LegalChunk.source_id.in_(matched_source_ids), 0.2),
        else_=0.0,
    )


def _to_search_result(
    *,
    chunk: LegalChunk,
    score: float,
    vector_score: float | None = None,
    trigram_score: float | None = None,
) -> LegalSearchResult:
    return LegalSearchResult(
        id=str(chunk.id),
        source_id=chunk.source_id,
        source_url=chunk.source_url,
        law_title=chunk.law_title,
        article_number=chunk.article_number,
        heading=chunk.heading,
        content=chunk.content,
        score=score,
        vector_score=vector_score,
        trigram_score=trigram_score,
    )


def _reciprocal_rank_fusion(
    vector_results: list[LegalSearchResult],
    text_results: list[LegalSearchResult],
    *,
    limit: int,
    rank_constant: int = 60,
) -> list[LegalSearchResult]:
    scores: dict[str, float] = {}
    results_by_id: dict[str, LegalSearchResult] = {}

    for results in (vector_results, text_results):
        for rank, result in enumerate(results, start=1):
            results_by_id[result.id] = result
            scores[result.id] = scores.get(result.id, 0.0) + (1 / (rank_constant + rank))

    ranked_ids = sorted(scores, key=scores.get, reverse=True)[:limit]
    return [
        LegalSearchResult(
            **{
                **results_by_id[result_id].__dict__,
                "score": scores[result_id],
            }
        )
        for result_id in ranked_ids
    ]

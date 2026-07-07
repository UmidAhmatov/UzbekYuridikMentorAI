from __future__ import annotations

import argparse
import asyncio
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import delete

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import AsyncSessionLocal
from app.models import LegalChunk
from app.services.legal_kb import LegalChunkPayload, upsert_chunks
from app.services.legal_sources import LEGAL_SOURCE_BY_KEY, LEGAL_SOURCES, LegalSourceDefinition

DEFAULT_LEX_ID = "-6257288"
DEFAULT_LEX_URL = f"https://lex.uz/docs/{DEFAULT_LEX_ID}"

ARTICLE_RE = re.compile(r"^(?P<number>\d+)-modda\.\s*(?P<title>.+)$", re.IGNORECASE)
OKOZ_RE = re.compile(r"\[\s*OKOZ:.*?\]", re.DOTALL | re.IGNORECASE)
WHITESPACE_RE = re.compile(r"[ \t]+")

BOILERPLATE_PATTERNS = (
    "Ҳужжатга таклиф юбориш",
    "Аудиони тинглаш",
    "Ҳужжат элементидан ҳавола олиш",
    "Hujjatga taklif yuborish",
    "Audioni tinglash",
    "Hujjat elementidan havola olish",
    "ONLINE TRANSLATE",
    "Кўриниш",
)


@dataclass(frozen=True)
class Article:
    number: str
    heading: str
    body: str


async def main() -> None:
    args = parse_args()
    if args.list_sources:
        for source in LEGAL_SOURCES:
            print(f"{source.key:26} {source.lex_id:10} {source.title}")
        return

    if args.all or args.codes:
        sources = list(LEGAL_SOURCES) if args.all else [
            LEGAL_SOURCE_BY_KEY[key]
            for key in args.codes
        ]
        results = await ingest_sources(
            sources,
            chunk_size=args.chunk_size,
            overlap=args.overlap,
            batch_size=args.batch_size,
            max_chunks=args.max_chunks,
            with_embeddings=not args.skip_embeddings,
            dry_run=args.dry_run,
        )
        print(f"Sources completed: {len(results)}/{len(sources)}")
        print(f"Total chunks upserted: {sum(result.upserted_count for result in results)}")
        return

    result = await ingest_document(
        url=args.url,
        source_id=args.source_id,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        batch_size=args.batch_size,
        max_chunks=args.max_chunks,
        with_embeddings=not args.skip_embeddings,
        dry_run=args.dry_run,
    )
    print(f"Fetched: {args.url}")
    print(f"Law title: {result.law_title}")
    print(f"Articles parsed: {result.article_count}")
    print(f"Chunks prepared: {result.chunk_count}")
    print(f"Embeddings: {'enabled' if result.with_embeddings else 'disabled'}")
    print(f"Chunks upserted: {result.upserted_count}")


@dataclass(frozen=True)
class IngestResult:
    law_title: str
    article_count: int
    chunk_count: int
    upserted_count: int
    with_embeddings: bool


async def ingest_document(
    *,
    url: str,
    source_id: str,
    chunk_size: int = 1800,
    overlap: int = 180,
    batch_size: int = 8,
    max_chunks: int | None = None,
    with_embeddings: bool = True,
    dry_run: bool = False,
    law_title_override: str | None = None,
) -> IngestResult:
    html = await fetch_html(url)
    law_title = law_title_override or extract_title(html)
    text = clean_text(extract_text(html))
    articles = extract_articles(text)
    chunks = build_chunks(
        articles,
        source_id=source_id,
        source_url=url,
        law_title=law_title,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    if max_chunks is not None:
        chunks = chunks[:max_chunks]

    total = 0
    if not dry_run:
        total = await ingest_chunks(
            chunks,
            batch_size=batch_size,
            with_embeddings=with_embeddings,
            cleanup_stale=max_chunks is None,
        )
    return IngestResult(
        law_title=law_title,
        article_count=len(articles),
        chunk_count=len(chunks),
        upserted_count=total,
        with_embeddings=with_embeddings,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest Lex.uz legal documents into legal_chunks.")
    parser.add_argument("--lex-id", default=DEFAULT_LEX_ID, help="Lex.uz document ID, for example -6257288.")
    parser.add_argument("--url", default=None, help="Full Lex.uz document URL. Overrides --lex-id.")
    parser.add_argument("--source-id", default=None, help="Stable source ID stored in legal_chunks.source_id.")
    parser.add_argument("--chunk-size", type=int, default=1800, help="Maximum chunk body size in characters.")
    parser.add_argument("--overlap", type=int, default=180, help="Overlap between split chunks in characters.")
    parser.add_argument("--batch-size", type=int, default=8, help="DB/embedding batch size.")
    parser.add_argument("--max-chunks", type=int, default=None, help="Limit chunks for smoke tests.")
    parser.add_argument("--skip-embeddings", action="store_true", help="Store chunks without BGE-m3 embeddings.")
    parser.add_argument("--all", action="store_true", help="Ingest every source from the built-in legal catalog.")
    parser.add_argument(
        "--codes",
        nargs="+",
        choices=sorted(LEGAL_SOURCE_BY_KEY),
        help="Ingest selected catalog keys, for example: labor family tax.",
    )
    parser.add_argument("--list-sources", action="store_true", help="Print built-in source keys and exit.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and parse without writing to PostgreSQL.")
    args = parser.parse_args()

    if args.all and args.codes:
        parser.error("--all and --codes cannot be used together")

    if args.url is None:
        args.url = f"https://lex.uz/docs/{args.lex_id}"

    if args.source_id is None:
        normalized_id = args.lex_id.strip().lstrip("-")
        args.source_id = f"lex-{normalized_id}"

    if args.chunk_size < 400:
        parser.error("--chunk-size must be at least 400")

    if args.overlap < 0 or args.overlap >= args.chunk_size:
        parser.error("--overlap must be non-negative and smaller than --chunk-size")

    if args.batch_size < 1:
        parser.error("--batch-size must be at least 1")

    return args


async def ingest_sources(
    sources: list[LegalSourceDefinition],
    *,
    chunk_size: int = 1800,
    overlap: int = 180,
    batch_size: int = 8,
    max_chunks: int | None = None,
    with_embeddings: bool = True,
    dry_run: bool = False,
) -> list[IngestResult]:
    results: list[IngestResult] = []
    for index, source in enumerate(sources, start=1):
        print(f"\n[{index}/{len(sources)}] {source.title}")
        result = await ingest_document(
            url=source.url,
            source_id=source.source_id,
            chunk_size=chunk_size,
            overlap=overlap,
            batch_size=batch_size,
            max_chunks=max_chunks,
            with_embeddings=with_embeddings,
            dry_run=dry_run,
            law_title_override=source.title,
        )
        results.append(result)
        print(
            f"Completed: articles={result.article_count}, "
            f"chunks={result.chunk_count}, upserted={result.upserted_count}"
        )
    return results


async def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": "UzbekMentorAI/0.1 legal RAG ingestion",
        "Accept-Language": "uz,en;q=0.8,ru;q=0.6",
    }
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True, headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


def extract_title(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    if soup.title and soup.title.string:
        cleaned = normalize_line(soup.title.string.replace("\xa0", " "))
        cleaned = re.sub(r"^\d{2}\.\d{2}\.\d{4}\.\s*", "", cleaned)
        cleaned = re.sub(r"^[A-ZА-Я0-9-]+-сон\s+\d{2}\.\d{2}\.\d{4}\.\s*", "", cleaned)
        if cleaned:
            return cleaned

    return "Lex.uz hujjati"


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    return soup.get_text("\n")


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = OKOZ_RE.sub("\n", text)
    lines = []

    for raw_line in text.splitlines():
        line = normalize_line(raw_line)
        if not line:
            continue
        if any(pattern in line for pattern in BOILERPLATE_PATTERNS):
            continue
        if line in {"Image", "Рус", "Ўзб", "O’zb", "O‘zb|Рус", "A"}:
            continue
        lines.append(line)

    return "\n".join(lines)


def normalize_line(line: str) -> str:
    return WHITESPACE_RE.sub(" ", line).strip()


def extract_articles(text: str) -> list[Article]:
    lines = text.splitlines()
    articles: list[Article] = []
    current_number: str | None = None
    current_heading: str | None = None
    current_body: list[str] = []

    for line in lines:
        match = ARTICLE_RE.match(line)
        if match:
            append_article(articles, current_number, current_heading, current_body)
            current_number = match.group("number")
            current_heading = line
            current_body = []
            continue

        if current_number is not None:
            current_body.append(line)

    append_article(articles, current_number, current_heading, current_body)
    return deduplicate_articles(articles)


def append_article(
    articles: list[Article],
    number: str | None,
    heading: str | None,
    body_lines: list[str],
) -> None:
    if number is None or heading is None:
        return

    body = "\n".join(body_lines).strip()
    body = remove_leading_toc_noise(body)
    if len(body) < 40:
        return

    articles.append(Article(number=number, heading=heading, body=body))


def remove_leading_toc_noise(body: str) -> str:
    lines = body.splitlines()
    while lines and (
        lines[0].isupper()
        or re.match(r"^[IVXLCDM]+\s+BO", lines[0], re.IGNORECASE)
        or re.match(r"^\d+-bob\.", lines[0], re.IGNORECASE)
        or re.match(r"^\d+-§\.", lines[0], re.IGNORECASE)
    ):
        lines.pop(0)

    return "\n".join(lines).strip()


def deduplicate_articles(articles: list[Article]) -> list[Article]:
    best_by_number: dict[str, Article] = {}
    for article in articles:
        current = best_by_number.get(article.number)
        if current is None or len(article.body) > len(current.body):
            best_by_number[article.number] = article

    return sorted(best_by_number.values(), key=lambda article: int(article.number))


def build_chunks(
    articles: Iterable[Article],
    *,
    source_id: str,
    source_url: str,
    law_title: str,
    chunk_size: int,
    overlap: int,
) -> list[LegalChunkPayload]:
    fetched_at = datetime.now(UTC).isoformat()
    chunks: list[LegalChunkPayload] = []

    for article in articles:
        parts = split_text(article.body, chunk_size=chunk_size, overlap=overlap)
        for part_index, part in enumerate(parts):
            content = f"{article.heading}\n\n{part}"
            chunks.append(
                LegalChunkPayload(
                    source_id=source_id,
                    source_url=source_url,
                    law_title=law_title,
                    article_number=article.number,
                    heading=article.heading,
                    content=content,
                    chunk_index=len(chunks),
                    metadata={
                        "lex_url": source_url,
                        "article_number": article.number,
                        "article_heading": article.heading,
                        "article_part": part_index,
                        "fetched_at": fetched_at,
                        "language": "uz-latin",
                    },
                )
            )

    return chunks


def split_text(text: str, *, chunk_size: int, overlap: int) -> list[str]:
    text = text.strip()
    if len(text) <= chunk_size:
        return [text]

    paragraphs = [paragraph.strip() for paragraph in text.split("\n") if paragraph.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            if current:
                chunks.append(current.strip())
                current = ""
            chunks.extend(split_long_paragraph(paragraph, chunk_size=chunk_size, overlap=overlap))
            continue

        candidate = f"{current}\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current.strip())
        current = paragraph

    if current:
        chunks.append(current.strip())

    if overlap == 0 or len(chunks) <= 1:
        return chunks

    overlapped: list[str] = []
    previous_tail = ""
    for chunk in chunks:
        combined = f"{previous_tail}\n{chunk}".strip() if previous_tail else chunk
        overlapped.append(combined)
        previous_tail = chunk[-overlap:]

    return overlapped


def split_long_paragraph(paragraph: str, *, chunk_size: int, overlap: int) -> list[str]:
    chunks = []
    start = 0
    while start < len(paragraph):
        end = min(start + chunk_size, len(paragraph))
        chunks.append(paragraph[start:end].strip())
        if end == len(paragraph):
            break
        start = max(0, end - overlap)

    return chunks


async def ingest_chunks(
    chunks: list[LegalChunkPayload],
    *,
    batch_size: int,
    with_embeddings: bool,
    cleanup_stale: bool,
) -> int:
    total = 0
    async with AsyncSessionLocal() as session:
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            total += await upsert_chunks(session, batch, with_embeddings=with_embeddings)
            await session.commit()
            print(f"Upserted batch {start // batch_size + 1}: {total}/{len(chunks)}")

        if cleanup_stale and chunks:
            await session.execute(
                delete(LegalChunk).where(
                    LegalChunk.source_id == chunks[0].source_id,
                    LegalChunk.chunk_index >= len(chunks),
                )
            )
            await session.commit()

    return total


if __name__ == "__main__":
    asyncio.run(main())

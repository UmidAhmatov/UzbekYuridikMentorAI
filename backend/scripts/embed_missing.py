from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.embedding_backfill import backfill_missing_embeddings
from app.services.legal_sources import LEGAL_SOURCE_BY_KEY


async def main() -> None:
    args = parse_args()
    source_id = LEGAL_SOURCE_BY_KEY[args.code].source_id if args.code else None
    completed = await backfill_missing_embeddings(
        batch_size=args.batch_size,
        max_chunks=args.max_chunks,
        source_id=source_id,
    )
    print(f"Done. Embeddings added: {completed}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill missing BGE-m3 legal chunk embeddings.")
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-chunks", type=int, default=None)
    parser.add_argument("--code", choices=sorted(LEGAL_SOURCE_BY_KEY), default=None)
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be at least 1")
    if args.max_chunks is not None and args.max_chunks < 1:
        parser.error("--max-chunks must be at least 1")
    return args


if __name__ == "__main__":
    asyncio.run(main())


from __future__ import annotations

from pydantic import BaseModel


class LegalSourceStatusSchema(BaseModel):
    key: str
    title: str
    lex_id: str
    source_id: str
    url: str
    category: str
    chunk_count: int
    embedding_count: int


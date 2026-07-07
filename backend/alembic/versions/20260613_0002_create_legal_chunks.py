"""create legal chunks

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-13 00:10:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "legal_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("law_title", sa.String(length=500), nullable=False),
        sa.Column("article_number", sa.String(length=64), nullable=True),
        sa.Column("heading", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("embedding", Vector(1024), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_legal_chunks")),
        sa.UniqueConstraint("source_id", "chunk_index", name="uq_legal_chunks_source_id_chunk_index"),
    )
    op.create_index(op.f("ix_legal_chunks_source_id"), "legal_chunks", ["source_id"], unique=False)
    op.create_index(op.f("ix_legal_chunks_article_number"), "legal_chunks", ["article_number"], unique=False)
    op.execute(
        "CREATE INDEX ix_legal_chunks_embedding_hnsw "
        "ON legal_chunks USING hnsw (embedding vector_cosine_ops)"
    )
    op.execute(
        "CREATE INDEX ix_legal_chunks_content_trgm "
        "ON legal_chunks USING gin (content gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX ix_legal_chunks_law_title_trgm "
        "ON legal_chunks USING gin (law_title gin_trgm_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_legal_chunks_law_title_trgm")
    op.execute("DROP INDEX IF EXISTS ix_legal_chunks_content_trgm")
    op.execute("DROP INDEX IF EXISTS ix_legal_chunks_embedding_hnsw")
    op.drop_index(op.f("ix_legal_chunks_article_number"), table_name="legal_chunks")
    op.drop_index(op.f("ix_legal_chunks_source_id"), table_name="legal_chunks")
    op.drop_table("legal_chunks")

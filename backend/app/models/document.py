from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.disclaimer import LEGAL_AI_DISCLAIMER
from app.database import Base

if TYPE_CHECKING:
    from app.models.chat import Chat
    from app.models.user import User


class DocumentType(str, enum.Enum):
    davo_arizasi = "davo_arizasi"
    shikoyat = "shikoyat"
    ishonchnoma = "ishonchnoma"
    mehnat_shartnomasi = "mehnat_shartnomasi"
    ijara_shartnomasi = "ijara_shartnomasi"
    sud_arizasi = "sud_arizasi"


document_type_enum = Enum(
    DocumentType,
    name="document_type",
    values_callable=lambda items: [item.value for item in items],
)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    chat_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chats.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    turi: Mapped[DocumentType] = mapped_column(document_type_enum, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    input_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    disclaimer: Mapped[str] = mapped_column(Text, nullable=False, default=LEGAL_AI_DISCLAIMER, server_default=LEGAL_AI_DISCLAIMER)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft", server_default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped[User | None] = relationship(back_populates="documents")
    chat: Mapped[Chat | None] = relationship(back_populates="documents")

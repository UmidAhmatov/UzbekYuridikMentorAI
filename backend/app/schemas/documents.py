from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models import DocumentType
from app.schemas.mentor import ResponseLanguage


DocumentFieldType = Literal["text", "textarea", "date", "select"]


class DocumentFieldSchema(BaseModel):
    name: str
    label: str
    field_type: DocumentFieldType
    required: bool
    placeholder: str | None = None
    help_text: str | None = None
    options: list[str] = Field(default_factory=list)


class DocumentTemplateSchema(BaseModel):
    type: DocumentType
    title: str
    description: str
    fields: list[DocumentFieldSchema]


class DocumentGenerateRequest(BaseModel):
    type: DocumentType
    values: dict[str, str] = Field(default_factory=dict)
    language: ResponseLanguage = ResponseLanguage.uz_latin


class LegalSourceSchema(BaseModel):
    id: str
    source_url: str
    law_title: str
    article_number: str | None
    heading: str | None


class GeneratedDocumentSchema(BaseModel):
    id: UUID
    type: DocumentType
    title: str
    content: str
    disclaimer: str
    sources: list[LegalSourceSchema]
    pdf_url: str

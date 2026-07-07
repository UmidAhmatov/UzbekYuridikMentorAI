from __future__ import annotations

import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.disclaimer import LEGAL_AI_DISCLAIMER
from app.database import get_db_session
from app.models import Document
from app.schemas.documents import (
    DocumentFieldSchema,
    DocumentGenerateRequest,
    DocumentTemplateSchema,
    GeneratedDocumentSchema,
    LegalSourceSchema,
)
from app.schemas.mentor import ResponseLanguage
from app.services.claude_client import ClaudeClientError, get_claude_client
from app.services.document_templates import (
    DOCUMENT_TEMPLATES,
    build_document_input,
    get_document_template,
    validate_document_values,
)
from app.services.legal_kb import LegalSearchResult, build_legal_context, retrieve
from app.services.localization import localize_text
from app.services.pdf import build_document_pdf
from app.services.prompts import build_document_system_prompt

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/templates", response_model=list[DocumentTemplateSchema])
async def list_document_templates(
    language: ResponseLanguage = Query(ResponseLanguage.uz_latin),
) -> list[DocumentTemplateSchema]:
    return [
        DocumentTemplateSchema(
            type=template.type,
            title=localize_text(template.title, language) or template.title,
            description=localize_text(template.description, language) or template.description,
            fields=[
                DocumentFieldSchema(
                    name=field.name,
                    label=localize_text(field.label, language) or field.label,
                    field_type=field.field_type,
                    required=field.required,
                    placeholder=localize_text(field.placeholder, language),
                    help_text=localize_text(field.help_text, language),
                    options=[localize_text(option, language) or option for option in field.options],
                )
                for field in template.fields
            ],
        )
        for template in DOCUMENT_TEMPLATES.values()
    ]


@router.post("/generate", response_model=GeneratedDocumentSchema)
async def generate_document(
    payload: DocumentGenerateRequest,
    db: AsyncSession = Depends(get_db_session),
) -> GeneratedDocumentSchema:
    template = get_document_template(payload.type)
    try:
        values = validate_document_values(template, payload.values)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    search_query = f"{template.legal_focus}. {build_document_input(template, values)}"
    legal_results = await retrieve(db, search_query)
    legal_context = build_legal_context(legal_results)
    system_prompt = build_document_system_prompt(
        document_title=localize_text(template.title, payload.language) or template.title,
        legal_context=legal_context,
        language=payload.language,
    )
    user_prompt = build_document_input(template, values)

    chunks: list[str] = []
    try:
        async for chunk in get_claude_client().stream_messages(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        ):
            chunks.append(chunk)
    except ClaudeClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    content = "".join(chunks).strip()
    if not content:
        raise HTTPException(status_code=502, detail="Claude hujjat matnini qaytarmadi.")

    sources = [_source_schema(result) for result in legal_results]
    localized_title = localize_text(template.title, payload.language) or template.title
    document = Document(
        turi=payload.type,
        title=localized_title,
        input_data={
            "values": values,
            "legal_sources": [source.model_dump() for source in sources],
        },
        content=content,
        disclaimer=LEGAL_AI_DISCLAIMER,
        status="draft",
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    return GeneratedDocumentSchema(
        id=document.id,
        type=document.turi,
        title=document.title,
        content=document.content,
        disclaimer=document.disclaimer,
        sources=sources,
        pdf_url=f"/api/documents/{document.id}/pdf",
    )


@router.get("/{document_id}/pdf")
async def download_document_pdf(
    document_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> Response:
    document = await db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Hujjat topilmadi.")

    pdf_bytes = await asyncio.to_thread(
        build_document_pdf,
        title=document.title,
        content=document.content,
        disclaimer=document.disclaimer,
    )
    filename = f"{document.turi.value}-{document.id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _source_schema(result: LegalSearchResult) -> LegalSourceSchema:
    return LegalSourceSchema(
        id=result.id,
        source_url=result.source_url,
        law_title=result.law_title,
        article_number=result.article_number,
        heading=result.heading,
    )

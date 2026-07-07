from __future__ import annotations

import unittest
import uuid
from unittest.mock import AsyncMock, patch

from app.core.disclaimer import LEGAL_AI_DISCLAIMER
from app.models import DocumentType
from app.schemas.documents import DocumentGenerateRequest
from app.services.document_templates import (
    DOCUMENT_TEMPLATES,
    get_document_template,
    validate_document_values,
)
from app.services.legal_kb import LegalSearchResult
from app.services.pdf import build_document_pdf


class FakeSession:
    def __init__(self) -> None:
        self.added = None

    def add(self, value) -> None:
        self.added = value

    async def commit(self) -> None:
        return None

    async def refresh(self, value) -> None:
        value.id = uuid.uuid4()


class FakeClaudeClient:
    async def stream_messages(self, **_kwargs):
        yield "TOSHKENT SHAHAR SUDIGA\n\n"
        yield "Arizachi: Ali Valiyev\n\nTalab: huquqni tiklash."


class DocumentTemplateTests(unittest.TestCase):
    def test_all_document_types_have_templates(self) -> None:
        self.assertEqual(set(DOCUMENT_TEMPLATES), set(DocumentType))

    def test_required_fields_are_validated(self) -> None:
        template = get_document_template(DocumentType.ishonchnoma)
        with self.assertRaisesRegex(ValueError, "Majburiy maydonlarni"):
            validate_document_values(template, {})

    def test_pdf_contains_unicode_document(self) -> None:
        pdf = build_document_pdf(
            title="Mehnat shartnomasi",
            content="Xodimga yillik mehnat ta'tili beriladi.",
            disclaimer=LEGAL_AI_DISCLAIMER,
        )
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertGreater(len(pdf), 1000)


class DocumentGenerationTests(unittest.IsolatedAsyncioTestCase):
    async def test_generated_document_has_sources_and_disclaimer(self) -> None:
        from app.api.documents import generate_document

        template = get_document_template(DocumentType.sud_arizasi)
        values = {
            field.name: f"{field.label} qiymati"
            for field in template.fields
            if field.required
        }
        source = LegalSearchResult(
            id=str(uuid.uuid4()),
            source_id="-6257288",
            source_url="https://lex.uz/docs/-6257288",
            law_title="O'zbekiston Respublikasining Mehnat kodeksi",
            article_number="1",
            heading="Mehnat qonunchiligi",
            content="Sinov konteksti",
            score=0.9,
        )
        session = FakeSession()

        with (
            patch("app.api.documents.retrieve", new=AsyncMock(return_value=[source])),
            patch("app.api.documents.get_claude_client", return_value=FakeClaudeClient()),
        ):
            result = await generate_document(
                DocumentGenerateRequest(type=DocumentType.sud_arizasi, values=values),
                db=session,
            )

        self.assertEqual(result.disclaimer, LEGAL_AI_DISCLAIMER)
        self.assertEqual(result.sources[0].article_number, "1")
        self.assertIn("TOSHKENT SHAHAR SUDIGA", result.content)
        self.assertIsNotNone(session.added)


if __name__ == "__main__":
    unittest.main()


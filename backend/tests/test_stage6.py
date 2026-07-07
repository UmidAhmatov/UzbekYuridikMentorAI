from __future__ import annotations

import unittest
import uuid
from unittest.mock import AsyncMock, patch

from app.core.disclaimer import LEGAL_AI_DISCLAIMER
from app.schemas.mentor import CareerRequest, ResponseLanguage, RoadmapRequest
from app.services.legal_kb import LegalSearchResult, _reciprocal_rank_fusion
from app.services.legal_sources import LEGAL_SOURCES
from app.services.localization import localize_text
from app.services.scheduler import MONTHLY_INGEST_JOB_ID, build_scheduler


class FakeClaudeClient:
    async def complete_message(self, **_kwargs) -> str:
        return "1. Hujjatlarni tayyorlang.\n2. Vakolatli organga topshiring."


class Stage6LocalizationTests(unittest.TestCase):
    def test_legal_source_catalog_has_unique_documents(self) -> None:
        self.assertEqual(len(LEGAL_SOURCES), 21)
        self.assertEqual(len({source.lex_id for source in LEGAL_SOURCES}), 21)
        water_source = next(source for source in LEGAL_SOURCES if source.key == "water")
        self.assertEqual(water_source.category, "law")
        institutional_laws = {
            source.key: source.lex_id
            for source in LEGAL_SOURCES
            if source.key in {"advocacy", "prosecutor_office", "courts"}
        }
        self.assertEqual(
            institutional_laws,
            {
                "advocacy": "-54503",
                "prosecutor_office": "-106197",
                "courts": "-5534923",
            },
        )

    def test_cyrillic_template_localization(self) -> None:
        self.assertEqual(
            localize_text("Mehnat shartnomasi", ResponseLanguage.uz_cyrillic),
            "Меҳнат шартномаси",
        )
        self.assertEqual(
            localize_text("Da'vo arizasi", ResponseLanguage.uz_cyrillic),
            "Даъво аризаси",
        )

    def test_russian_template_localization(self) -> None:
        self.assertEqual(
            localize_text("Ishonchnoma", ResponseLanguage.ru),
            "Доверенность",
        )

    def test_monthly_scheduler_configuration(self) -> None:
        scheduler = build_scheduler()
        jobs = scheduler.get_jobs()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].id, MONTHLY_INGEST_JOB_ID)
        self.assertIn("day='1'", str(jobs[0].trigger))
        self.assertIn("hour='3'", str(jobs[0].trigger))
        self.assertEqual(jobs[0].max_instances, 1)
        self.assertTrue(jobs[0].coalesce)

    def test_rank_fusion_keeps_text_only_code_results(self) -> None:
        vector_result = LegalSearchResult(
            id="labor",
            source_id="lex-6257288",
            source_url="https://lex.uz/docs/-6257288",
            law_title="Mehnat kodeksi",
            article_number="1",
            heading=None,
            content="Mehnat",
            score=0.9,
        )
        text_result = LegalSearchResult(
            id="tax",
            source_id="lex-4674902",
            source_url="https://lex.uz/docs/-4674902",
            law_title="Soliq kodeksi",
            article_number="85",
            heading=None,
            content="Soliq majburiyati",
            score=0.8,
        )
        fused = _reciprocal_rank_fusion([vector_result], [text_result], limit=2)
        self.assertEqual({result.id for result in fused}, {"labor", "tax"})


class Stage6EndpointTests(unittest.IsolatedAsyncioTestCase):
    async def test_roadmap_returns_rag_sources_and_disclaimer(self) -> None:
        from app.api.roadmap import generate_roadmap

        source = LegalSearchResult(
            id=str(uuid.uuid4()),
            source_id="lex-6257288",
            source_url="https://lex.uz/docs/-6257288",
            law_title="O'zbekiston Respublikasining Mehnat kodeksi",
            article_number="217",
            heading="Har yilgi mehnat ta'tili",
            content="Sinov konteksti",
            score=0.9,
        )
        with (
            patch("app.api.roadmap.retrieve", new=AsyncMock(return_value=[source])),
            patch("app.api.roadmap.get_claude_client", return_value=FakeClaudeClient()),
        ):
            result = await generate_roadmap(
                RoadmapRequest(
                    situation="Ish beruvchi mehnat ta'tilini bermayapti.",
                    goal="Ta'til huquqini amalga oshirish",
                ),
                db=object(),
            )

        self.assertEqual(result.disclaimer, LEGAL_AI_DISCLAIMER)
        self.assertEqual(result.sources[0].article_number, "217")
        self.assertIn("1.", result.content)

    async def test_career_returns_selected_language_title(self) -> None:
        from app.api.career import advise_career

        with patch("app.api.career.get_claude_client", return_value=FakeClaudeClient()):
            result = await advise_career(
                CareerRequest(
                    current_role="Talaba",
                    experience_level="Boshlang'ich",
                    target_role="Frontend dasturchi",
                    skills="HTML, CSS, JavaScript",
                    language=ResponseLanguage.ru,
                )
            )

        self.assertEqual(result.title, "Карьерный план действий")
        self.assertEqual(result.disclaimer, LEGAL_AI_DISCLAIMER)
        self.assertEqual(result.sources, [])


if __name__ == "__main__":
    unittest.main()

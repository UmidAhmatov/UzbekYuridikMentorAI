from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ResponseLanguage(str, Enum):
    uz_latin = "uz-latin"
    uz_cyrillic = "uz-cyrillic"
    ru = "ru"


class AdviceSourceSchema(BaseModel):
    id: str
    source_url: str
    law_title: str
    article_number: str | None
    heading: str | None


class AdviceResponse(BaseModel):
    title: str
    content: str
    disclaimer: str
    sources: list[AdviceSourceSchema] = Field(default_factory=list)


class RoadmapRequest(BaseModel):
    situation: str = Field(min_length=10, max_length=8000)
    goal: str = Field(min_length=3, max_length=2000)
    region: str | None = Field(default=None, max_length=255)
    event_date: str | None = Field(default=None, max_length=100)
    available_documents: str | None = Field(default=None, max_length=3000)
    language: ResponseLanguage = ResponseLanguage.uz_latin


class CareerRequest(BaseModel):
    current_role: str = Field(min_length=2, max_length=255)
    experience_level: str = Field(min_length=2, max_length=100)
    target_role: str = Field(min_length=2, max_length=255)
    skills: str = Field(min_length=2, max_length=3000)
    region: str | None = Field(default=None, max_length=255)
    employment_type: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=3000)
    language: ResponseLanguage = ResponseLanguage.uz_latin


from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "UzbekMentorAI"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://uzbekmentor:uzbekmentor_dev_password@db:5432/uzbekmentor"
    anthropic_api_key: str | None = None
    anthropic_api_url: str = "https://api.anthropic.com/v1/messages"
    anthropic_api_version: str = "2023-06-01"
    claude_model: str = "claude-sonnet-4-6"
    claude_max_tokens: int = 1600
    embedding_model_name: str = "BAAI/bge-m3"
    embedding_dimension: int = 1024
    backend_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    scheduler_enabled: bool = True
    scheduler_timezone: str = "Asia/Tashkent"
    monthly_ingest_hour: int = 3
    monthly_ingest_minute: int = 0
    ingest_batch_size: int = 8

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


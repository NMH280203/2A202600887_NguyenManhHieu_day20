"""Application configuration.

Keep config small and explicit. Do not read environment variables directly in agents.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables or `.env`."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="local", validation_alias="APP_ENV")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", validation_alias="OPENAI_MODEL")

    langsmith_api_key: str | None = Field(default=None, validation_alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field(default="multi-agent-research-lab", validation_alias="LANGSMITH_PROJECT")

    tavily_api_key: str | None = Field(default=None, validation_alias="TAVILY_API_KEY")
    tavily_max_query_length: int = Field(
        default=380, ge=50, le=400, validation_alias="TAVILY_MAX_QUERY_LENGTH"
    )

    use_critic: bool = Field(default=True, validation_alias="USE_CRITIC")
    min_citation_coverage: float = Field(
        default=0.5, ge=0.0, le=1.0, validation_alias="MIN_CITATION_COVERAGE"
    )
    max_writer_revisions: int = Field(
        default=2, ge=0, le=5, validation_alias="MAX_WRITER_REVISIONS"
    )

    max_iterations: int = Field(default=10, ge=1, le=20, validation_alias="MAX_ITERATIONS")
    timeout_seconds: int = Field(default=60, ge=5, le=600, validation_alias="TIMEOUT_SECONDS")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables and `.env`.
    """

    openrouter_api_key: str = Field(..., alias="OPENROUTER_API_KEY")
    llm_model: str = Field("qwen/qwen2.5-7b-instruct", alias="LLM_MODEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance so configuration is created once per process.
    """

    return Settings()

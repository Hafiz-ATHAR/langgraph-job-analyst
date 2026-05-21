from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: str = "development"

    mlflow_tracking_uri: str
    mlflow_experiment: str

    tavily_api_key: str

    local_llm: str = "llama3.1"

    cors_origins: list[str] = ["*"]

    prompt_alias: str = "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]

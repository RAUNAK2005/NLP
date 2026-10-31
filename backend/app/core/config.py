from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Synthetic Dataset Evaluation Framework"
    environment: str = "development"
    backend_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    database_url: str = "sqlite:///./nlp_eval.db"
    max_file_size_mb: int = 25
    max_rows: int = 20_000
    default_sample_size: int = 1_000
    random_seed: int = 42
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    fidelity_weight: float = Field(default=0.4, ge=0, le=1)
    diversity_weight: float = Field(default=0.3, ge=0, le=1)
    utility_weight: float = Field(default=0.3, ge=0, le=1)

    @property
    def cors_origins(self) -> list[str | AnyHttpUrl]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


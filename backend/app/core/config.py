from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env.local", PROJECT_ROOT / ".env"),
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://localhost/leaseai"
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    object_storage_bucket: str = "lease-documents"
    jwks_url: str = "https://conxwmnjhntbzftwgxig.supabase.co/auth/v1/.well-known/jwks.json"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8081"]
    demo_mode: bool = True
    demo_latency_ms: int = 600


settings = Settings()

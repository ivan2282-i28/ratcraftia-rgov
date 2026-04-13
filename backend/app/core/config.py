from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path


_DEFAULT_PUSH_PRIVATE_KEY = Path(__file__).resolve().with_name("dev_vapid_private.pem")
_DEFAULT_PUSH_PUBLIC_KEY = (
    "BMPFNftCVv-LfTcYGdyj3Kaq2WfBYGDuyn3BHR3lPFEDEtXVOCcXnuicuMO3c0QuZwlQfLpy4QauD4IvFlXqby0"
)


@dataclass(frozen=True)
class Settings:
    app_name: str
    secret_key: str
    algorithm: str
    access_token_ttl_minutes: int
    did_token_ttl_minutes: int
    oauth_code_ttl_minutes: int
    database_url: str
    cors_origins_raw: str
    local_timezone: str
    push_public_key: str
    push_private_key: str
    push_contact_email: str

    @property
    def cors_origins(self) -> list[str]:
        raw = [item.strip() for item in self.cors_origins_raw.split(",")]
        return [item for item in raw if item]

    @property
    def push_notifications_enabled(self) -> bool:
        return bool(self.push_public_key and self.push_private_key)


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name="RGOV - Ratcraftia Government Web Portal",
        secret_key=os.getenv("RGOV_SECRET_KEY", "ratcraftia-development-secret-key"),
        algorithm=os.getenv("RGOV_JWT_ALGORITHM", "HS256"),
        access_token_ttl_minutes=int(os.getenv("RGOV_ACCESS_TTL_MINUTES", "720")),
        did_token_ttl_minutes=int(os.getenv("RGOV_DID_TTL_MINUTES", "10")),
        oauth_code_ttl_minutes=int(os.getenv("RGOV_OAUTH_CODE_TTL_MINUTES", "5")),
        database_url=os.getenv("RGOV_DATABASE_URL", "sqlite:///./data/rgov.db"),
        cors_origins_raw=os.getenv(
            "RGOV_CORS_ORIGINS",
            "http://localhost:8080,http://127.0.0.1:8080,http://localhost:3000,*",
        ),
        local_timezone=os.getenv("RGOV_LOCAL_TIMEZONE", "Europe/Moscow"),
        push_public_key=os.getenv("RGOV_PUSH_PUBLIC_KEY", _DEFAULT_PUSH_PUBLIC_KEY),
        push_private_key=os.getenv("RGOV_PUSH_PRIVATE_KEY", str(_DEFAULT_PUSH_PRIVATE_KEY)),
        push_contact_email=os.getenv("RGOV_PUSH_CONTACT_EMAIL", "notifications@ratcraftia.local"),
    )


def reset_settings_cache() -> None:
    get_settings.cache_clear()

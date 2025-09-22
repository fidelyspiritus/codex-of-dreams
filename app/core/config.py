# app/core/config.py
from __future__ import annotations

from pathlib import Path
from typing import Any, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# МОДУЛЬНЫЕ КОНСТАНТЫ — Path
ROOT_PATH = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT_PATH / "data"
ASSETS_PATH = ROOT_PATH / "assets"

class Settings(BaseSettings):
    # читаем .env; игнорируем лишние ключи
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # чтобы CLI-скрипты могли запускаться без токена
    BOT_TOKEN: str = ""

    # ПУТИ (строки), вычислены из *_PATH
    DATA_DIR: str = str(DATA_PATH)
    MOUNT_SKILLS_DIR: str = str(DATA_PATH / "mount_skills")
    ASSETS_DIR: str = str(ASSETS_PATH)

    # Админ-флаг и список ID
    ENABLE_ADMIN_TOOLS: bool = Field(default=False)
    ADMIN_IDS: List[int] = Field(default_factory=list)

    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def _parse_admin_ids(cls, v: Any) -> list[int]:
        match v:
            case None | "":
                return []
            case list() | tuple():
                return [int(x) for x in v]
            case int():
                return [v]
            case str() as s:
                s = s.strip()
                if s.startswith("[") and s.endswith("]"):
                    import json
                    arr = json.loads(s)
                    if not isinstance(arr, list):
                        raise ValueError("ADMIN_IDS JSON must be a list")
                    return [int(x) for x in arr]
                return [int(x.strip()) for x in s.split(",") if x.strip()]
            case _:
                raise ValueError("Unsupported ADMIN_IDS format")

settings = Settings()

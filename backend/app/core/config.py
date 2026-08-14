from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_id: int
    api_hash: str
    session_path: Path = BACKEND_DIR / "data" / "manager.session"

    db_path: Path = BACKEND_DIR / "data" / "tracker.db"

    timezone: str = "Asia/Tashkent"

    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: list[str] = ["*"]
    allowed_hosts: list[str] = ["*"]

    admin_username: str
    admin_password_hash: str
    jwt_secret: str
    jwt_ttl_minutes: int = 720
    cookie_name: str = "session"
    cookie_secure: bool = True


settings = Settings()

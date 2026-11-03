"""Настройки из переменных окружения (.env). Секреты живут только здесь и не логируются."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _bool(value: str | None, default: bool) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str = field(repr=False, default="")
    model_triage: str = "claude-haiku-5-5"
    model_analyze: str = "claude-sonnet-5-5"
    model_weekly: str = "claude-opus-5-5"
    daily_budget_usd: float = 3.0
    monthly_budget_usd: float = 60.0
    mail_transport: str = "smtp"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_app_password: str = field(repr=False, default="")
    mail_from: str = ""
    digest_to: str = ""
    contact_email: str = ""
    timezone: str = "America/New_York"
    show_understanding_only: bool = True
    openalex_mailto: str = ""
    acled_api_key: str = field(repr=False, default="")
    db_path: Path = PROJECT_ROOT / "data" / "madam.sqlite3"

    @property
    def mail_ready(self) -> bool:
        return bool(self.smtp_user and self.smtp_app_password and self.digest_to)


def load_settings(env_file: Path | None = None) -> Settings:
    load_dotenv(env_file or PROJECT_ROOT / ".env", override=False)
    e = os.environ.get
    db = Path(e("DB_PATH") or "data/madam.sqlite3")
    return Settings(
        anthropic_api_key=e("ANTHROPIC_API_KEY", ""),
        model_triage=e("MODEL_TRIAGE") or Settings.model_triage,
        model_analyze=e("MODEL_ANALYZE") or Settings.model_analyze,
        model_weekly=e("MODEL_WEEKLY") or Settings.model_weekly,
        daily_budget_usd=float(e("DAILY_BUDGET_USD") or 3),
        monthly_budget_usd=float(e("MONTHLY_BUDGET_USD") or 60),
        mail_transport=e("MAIL_TRANSPORT") or "smtp",
        smtp_host=e("SMTP_HOST") or "smtp.gmail.com",
        smtp_port=int(e("SMTP_PORT") or 587),
        smtp_user=e("SMTP_USER", ""),
        smtp_app_password=(e("SMTP_APP_PASSWORD") or "").replace(" ", ""),
        mail_from=e("MAIL_FROM") or e("SMTP_USER", ""),
        digest_to=e("DIGEST_TO", ""),
        contact_email=e("CONTACT_EMAIL_FOR_USER_AGENT", ""),
        timezone=e("TIMEZONE") or "America/New_York",
        show_understanding_only=_bool(e("SHOW_UNDERSTANDING_ONLY"), True),
        openalex_mailto=e("OPENALEX_MAILTO", ""),
        acled_api_key=e("ACLED_API_KEY", ""),
        db_path=db if db.is_absolute() else PROJECT_ROOT / db,
    )

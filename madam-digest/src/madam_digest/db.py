"""SQLite: подключение и применение схемы."""

from __future__ import annotations

import sqlite3
from importlib import resources
from pathlib import Path

from .settings import PROJECT_ROOT

SCHEMA_VERSION = 1


def schema_sql() -> str:
    repo_copy = PROJECT_ROOT / "sql" / "schema.sql"
    if repo_copy.exists():
        return repo_copy.read_text(encoding="utf-8")
    return resources.files("madam_digest").joinpath("schema.sql").read_text(encoding="utf-8")


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(path: Path) -> list[str]:
    """Создаёт таблицы, если их нет. Повторный вызов безопасен. Возвращает список таблиц."""
    with connect(path) as conn:
        conn.executescript(schema_sql())
        if conn.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0] == 0:
            conn.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    return [r[0] for r in rows]

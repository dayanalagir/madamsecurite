"""Командная строка `madam`.

На этапе 0 работают `config check`, `db init` и `mail status`; остальное — заглушки с номером этапа.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence

from . import __version__
from .config import load_config
from .db import init_db
from .settings import load_settings

NOT_READY_EXIT = 3
DIGEST_TYPES = ["daily", "friday", "topic", "weekly", "monthly"]


def _not_ready(stage: int, what: str) -> Callable[[argparse.Namespace], int]:
    def run(_: argparse.Namespace) -> int:
        print(f"«{what}» появится на этапе {stage}.", file=sys.stderr)
        return NOT_READY_EXIT

    return run


def cmd_config_check(_: argparse.Namespace) -> int:
    cfg = load_config()
    by_stream: dict[str, list[str]] = {}
    for t in cfg.topics.topics:
        by_stream.setdefault(t.stream, []).append(t.id)
    counts = (len(cfg.topics.topics), len(cfg.sources.sources), len(cfg.schedule.letters))
    print("Топиков: {}; источников: {}; писем: {}".format(*counts))
    for stream, ids in by_stream.items():
        print(f"  поток {stream}: {', '.join(ids)}")
    unverified = sum(1 for a in cfg.anchors if not a.get("verified_on"))
    print(f"Якорей без проверки: {unverified} из {len(cfg.anchors)}")
    print("Конфиги в порядке.")
    return 0


def cmd_db_init(_: argparse.Namespace) -> int:
    settings = load_settings()
    tables = init_db(settings.db_path)
    print(f"База: {settings.db_path}\nТаблиц: {len(tables)}")
    return 0


def cmd_mail_status(_: argparse.Namespace) -> int:
    s = load_settings()
    print(f"Транспорт: {s.mail_transport}; сервер: {s.smtp_host}:{s.smtp_port}")
    print(f"Отправитель: {s.mail_from or 'не задан'}; получатель: {s.digest_to or 'не задан'}")
    print("Пароль приложения: " + ("задан" if s.smtp_app_password else "не задан (SMTP_APP_PASSWORD в .env)"))
    return 0 if s.mail_ready else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="madam", description="Агрегатор новостей и дайджестов Madam Securité.")
    p.add_argument("--version", action="version", version=f"madam-digest {__version__}")
    sub = p.add_subparsers(dest="command", required=True, metavar="КОМАНДА")

    def add(name: str, helptext: str, func: Callable[[argparse.Namespace], int]) -> argparse.ArgumentParser:
        sp = sub.add_parser(name, help=helptext, description=helptext)
        sp.set_defaults(func=func)
        return sp

    add("fetch", "собрать новое из источников", _not_ready(1, "fetch"))
    add("analyze", "триаж и анализ сюжетов", _not_ready(2, "analyze"))

    dg = add("digest", "собрать письмо", _not_ready(2, "digest"))
    dg.add_argument("type", choices=DIGEST_TYPES, help="тип письма")
    dg.add_argument("topic", nargs="?", help="топик для тематического дайджеста")
    dg.add_argument(
        "--stream",
        choices=["madam", "space"],
        default="madam",
        help="поток: международная повестка (madam) или космос (space)",
    )
    mode = dg.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="сохранить HTML в out/, не отправляя")
    mode.add_argument("--send", action="store_true", help="отправить письмо")

    al = add("alerts", "проверить условия алертов", _not_ready(5, "alerts"))
    al.add_argument("action", choices=["check"])
    src = add("sources", "проверить здоровье источников", _not_ready(1, "sources check"))
    src.add_argument("action", choices=["check"])
    gl = add("glossary", "показать непроверенные записи глоссария", _not_ready(2, "glossary check"))
    gl.add_argument("action", choices=["check"])
    bf = add("backfill", "заполнить базу за прошедшие дни", _not_ready(4, "backfill"))
    bf.add_argument("--days", type=int, default=7)
    add("test-mail", "отправить тестовое письмо с примером вёрстки", _not_ready(2, "test-mail"))

    cf = add("config", "проверить конфиги", cmd_config_check)
    cf.add_argument("action", choices=["check"])
    db = add("db", "создать или обновить базу SQLite", cmd_db_init)
    db.add_argument("action", choices=["init"])
    ml = add("mail", "показать настройки почты (без пароля)", cmd_mail_status)
    ml.add_argument("action", choices=["status"])
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

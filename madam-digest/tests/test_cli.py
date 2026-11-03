import pytest

from madam_digest.cli import NOT_READY_EXIT, build_parser, main

COMMANDS = [
    "fetch",
    "analyze",
    "digest",
    "alerts",
    "sources",
    "glossary",
    "backfill",
    "test-mail",
    "config",
    "db",
    "mail",
]


def test_help_lists_all_commands(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    for name in COMMANDS:
        assert name in out


def test_digest_accepts_both_streams():
    args = build_parser().parse_args(["digest", "daily", "--stream", "space", "--dry-run"])
    assert args.stream == "space" and args.dry_run


def test_digest_rejects_send_with_dry_run():
    with pytest.raises(SystemExit):
        build_parser().parse_args(["digest", "daily", "--dry-run", "--send"])


def test_unbuilt_commands_say_which_stage(capsys):
    assert main(["fetch"]) == NOT_READY_EXIT
    assert "этапе 1" in capsys.readouterr().err


def test_config_check_passes(capsys):
    assert main(["config", "check"]) == 0
    assert "Конфиги в порядке" in capsys.readouterr().out


def test_db_init_creates_database(isolated_env):
    assert main(["db", "init"]) == 0
    assert (isolated_env / "test.sqlite3").exists()


def test_mail_status_without_password_is_not_ready(capsys):
    assert main(["mail", "status"]) == 1
    assert "не задан" in capsys.readouterr().out

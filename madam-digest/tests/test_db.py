from madam_digest.db import connect, init_db

EXPECTED = {
    "sources",
    "fetch_log",
    "articles",
    "stories",
    "story_articles",
    "analyses",
    "scores",
    "digests",
    "digest_items",
    "feedback",
    "taste_profile",
    "treaties",
    "treaty_checks",
    "events_calendar",
    "anchors",
    "issues_counter",
    "runs",
    "cost_log",
}


def test_schema_has_all_tables(tmp_path):
    tables = set(init_db(tmp_path / "db.sqlite3"))
    assert tables >= EXPECTED


def test_init_is_idempotent(tmp_path):
    path = tmp_path / "db.sqlite3"
    init_db(path)
    init_db(path)
    with connect(path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0] == 1


def test_one_digest_per_type_stream_period(tmp_path):
    path = tmp_path / "db.sqlite3"
    init_db(path)
    with connect(path) as conn:
        conn.execute("INSERT INTO digests (type, stream, period_key) VALUES ('daily', 'madam', '2026-11-03')")
        conn.execute("INSERT INTO digests (type, stream, period_key) VALUES ('daily', 'space', '2026-11-03')")
        conn.execute(
            "INSERT OR IGNORE INTO digests (type, stream, period_key) VALUES ('daily', 'madam', '2026-11-03')"
        )
        assert conn.execute("SELECT COUNT(*) FROM digests").fetchone()[0] == 2

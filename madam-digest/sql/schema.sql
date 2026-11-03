-- Схема SQLite (раздел 13). Применяется идемпотентно командой `madam db init`.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL);

CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, url TEXT NOT NULL, type TEXT NOT NULL,
  lang TEXT, region TEXT, stream TEXT NOT NULL DEFAULT 'madam', tier INTEGER NOT NULL DEFAULT 2,
  paywall INTEGER NOT NULL DEFAULT 0, fetch_every_minutes INTEGER NOT NULL DEFAULT 60,
  etag TEXT, last_modified TEXT, last_ok_at TEXT, error_count INTEGER NOT NULL DEFAULT 0, notes TEXT
);

CREATE TABLE IF NOT EXISTS fetch_log (
  id INTEGER PRIMARY KEY, source_id TEXT REFERENCES sources(id), started_at TEXT NOT NULL,
  status INTEGER, items_new INTEGER DEFAULT 0, error TEXT
);

CREATE TABLE IF NOT EXISTS articles (
  id INTEGER PRIMARY KEY, url TEXT NOT NULL, canonical_url TEXT NOT NULL UNIQUE, title TEXT NOT NULL,
  outlet TEXT, source_id TEXT REFERENCES sources(id), lang TEXT, stream TEXT,
  published_at TEXT, fetched_at TEXT NOT NULL, snippet TEXT, text_hash TEXT,
  tier INTEGER, paywall INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at);

CREATE TABLE IF NOT EXISTS stories (
  id INTEGER PRIMARY KEY, stream TEXT NOT NULL DEFAULT 'madam', first_seen TEXT NOT NULL,
  last_updated TEXT NOT NULL, main_article_id INTEGER REFERENCES articles(id), status TEXT NOT NULL DEFAULT 'new'
);

CREATE TABLE IF NOT EXISTS story_articles (
  story_id INTEGER NOT NULL REFERENCES stories(id), article_id INTEGER NOT NULL REFERENCES articles(id),
  PRIMARY KEY (story_id, article_id)
);

CREATE TABLE IF NOT EXISTS analyses (
  id INTEGER PRIMARY KEY, story_id INTEGER NOT NULL REFERENCES stories(id), model TEXT NOT NULL,
  prompt_version TEXT NOT NULL, json TEXT NOT NULL, created_at TEXT NOT NULL, cost REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS scores (
  story_id INTEGER PRIMARY KEY REFERENCES stories(id), base REAL NOT NULL, taste_adj REAL DEFAULT 0,
  penalty REAL DEFAULT 0, total REAL NOT NULL, computed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS digests (
  id INTEGER PRIMARY KEY, type TEXT NOT NULL, stream TEXT NOT NULL DEFAULT 'madam', period_key TEXT NOT NULL,
  sent_at TEXT, subject TEXT, message_id TEXT, status TEXT NOT NULL DEFAULT 'pending',
  UNIQUE (type, stream, period_key)
);

CREATE TABLE IF NOT EXISTS digest_items (
  digest_id INTEGER NOT NULL REFERENCES digests(id), story_id INTEGER NOT NULL REFERENCES stories(id),
  position INTEGER NOT NULL, PRIMARY KEY (digest_id, story_id)
);

CREATE TABLE IF NOT EXISTS feedback (
  id INTEGER PRIMARY KEY, story_id INTEGER NOT NULL REFERENCES stories(id), action TEXT NOT NULL, ts TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS taste_profile (feature TEXT PRIMARY KEY, weight REAL NOT NULL DEFAULT 0, updated_at TEXT);

CREATE TABLE IF NOT EXISTS treaties (
  id TEXT PRIMARY KEY, name_ru TEXT NOT NULL, name_orig TEXT, year_signed INTEGER, parties TEXT,
  what_it_prohibits_or_limits TEXT, how_verified TEXT, status TEXT NOT NULL DEFAULT 'needs_human_check',
  status_source_url TEXT, status_checked_at TEXT, notes TEXT
);

CREATE TABLE IF NOT EXISTS treaty_checks (
  id INTEGER PRIMARY KEY, treaty_id TEXT NOT NULL REFERENCES treaties(id), checked_at TEXT NOT NULL,
  source_url TEXT, content_hash TEXT, diff TEXT
);

CREATE TABLE IF NOT EXISTS events_calendar (
  id INTEGER PRIMARY KEY, date TEXT NOT NULL, title TEXT NOT NULL, org TEXT, source_url TEXT,
  stream TEXT, topics TEXT, verified_on TEXT
);

CREATE TABLE IF NOT EXISTS anchors (
  id INTEGER PRIMARY KEY, month_day TEXT NOT NULL, title TEXT NOT NULL, topics TEXT, verified_on TEXT
);

CREATE TABLE IF NOT EXISTS issues_counter (series TEXT PRIMARY KEY, last_number INTEGER NOT NULL DEFAULT 0, last_date TEXT);

CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY, command TEXT, started_at TEXT NOT NULL, finished_at TEXT, stats_json TEXT, errors_json TEXT
);

CREATE TABLE IF NOT EXISTS cost_log (
  id INTEGER PRIMARY KEY, ts TEXT NOT NULL, model TEXT NOT NULL, purpose TEXT,
  input_tokens INTEGER, output_tokens INTEGER, usd REAL NOT NULL DEFAULT 0
);

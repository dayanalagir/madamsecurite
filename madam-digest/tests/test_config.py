from datetime import date

import pytest
import yaml

from madam_digest.config import CONFIG_DIR, load_config


def test_all_configs_load():
    cfg = load_config()
    assert len(cfg.topics.topics) == 10
    assert "Механизм, не вердикт" in cfg.brand


def test_space_is_its_own_stream():
    cfg = load_config()
    streams = {t.id: t.stream for t in cfg.topics.topics}
    assert streams["space"] == "space"
    assert all(s == "madam" for tid, s in streams.items() if tid != "space")
    assert cfg.schedule.streams["space"].subject != cfg.schedule.streams["madam"].subject


def test_each_stream_has_its_own_morning_letter():
    cfg = load_config()
    morning = {(x.stream, x.id) for x in cfg.schedule.letters if x.id in {"daily", "space_daily"}}
    assert morning == {("madam", "daily"), ("space", "space_daily")}


def test_no_unverified_sources_committed():
    # На этапе 0 список пуст: адреса добавляются только после живой проверки (этап 1).
    assert load_config().sources.sources == []


def test_anchors_start_unverified():
    assert all(a["verified_on"] is None for a in load_config().anchors)


def test_unknown_source_in_topic_is_rejected(tmp_path):
    for f in CONFIG_DIR.iterdir():
        (tmp_path / f.name).write_bytes(f.read_bytes())
    topics = yaml.safe_load((tmp_path / "topics.yaml").read_text(encoding="utf-8"))
    topics["topics"][0]["sources"] = ["no_such_source"]
    (tmp_path / "topics.yaml").write_text(yaml.safe_dump(topics, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match="неизвестные источники"):
        load_config(tmp_path)


def test_friday_pack_first_issue():
    fp = load_config().schedule.friday_pack
    assert fp.first_issue_number == 1 and fp.first_issue_draft_date == date(2026, 11, 5)

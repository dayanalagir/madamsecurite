"""Загрузка и проверка YAML-конфигов из папки config/."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .settings import PROJECT_ROOT

CONFIG_DIR = PROJECT_ROOT / "config"
Stream = Literal["madam", "space"]
Cluster = Literal["mech", "self", "news", "cur", "salon", "serial"]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Topic(_Strict):
    id: str
    name_ru: str
    stream: Stream
    weight: float = 1.0
    keywords: list[str] = Field(default_factory=list)
    exclude: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    rubrics: list[str] = Field(default_factory=list)
    cluster: Cluster
    account: Literal["p", "m", "b"]
    subtopics: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    rule: str | None = None


class TopicsFile(_Strict):
    clusters: list[Cluster]
    topics: list[Topic]

    @model_validator(mode="after")
    def unique_ids(self) -> TopicsFile:
        ids = [t.id for t in self.topics]
        if len(ids) != len(set(ids)):
            raise ValueError("повторяющиеся id топиков")
        return self


class Source(_Strict):
    id: str
    name: str
    url: str
    type: Literal["rss", "atom", "api", "html"]
    lang: str
    region: str = "global"
    stream: Stream
    topics: list[str]
    tier: Literal[1, 2, 3]
    paywall: bool = False
    fetch_every_minutes: int = 60
    notes: str = ""
    selectors: dict[str, str] | None = None


class SourcesFile(_Strict):
    sources: list[Source]


class StreamCfg(_Strict):
    name_ru: str
    subject: str
    topics: list[str]


class Letter(_Strict):
    id: str
    stream: Literal["madam", "space", "any"]
    name_ru: str
    days: list[Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"]] = Field(default_factory=list)
    time: str | None = None
    day_of_month: int | None = None
    max_per_day: int | None = None
    draws_from: list[Stream] = Field(default_factory=list)


class FridayPack(_Strict):
    first_issue_number: int
    first_issue_draft_date: date


class Schedule(_Strict):
    timezone: str
    streams: dict[Stream, StreamCfg]
    letters: list[Letter]
    topic_rotation: dict[str, str]
    friday_pack: FridayPack


class Config(BaseModel):
    topics: TopicsFile
    sources: SourcesFile
    schedule: Schedule
    glossary: dict
    anchors: list[dict]
    categories: dict
    formats: dict
    watchlist: dict
    brand: str

    @model_validator(mode="after")
    def cross_refs(self) -> Config:
        topic_ids = {t.id for t in self.topics.topics}
        source_ids = {s.id for s in self.sources.sources}
        for t in self.topics.topics:
            missing = set(t.sources) - source_ids
            if missing:
                raise ValueError(f"топик {t.id}: неизвестные источники {sorted(missing)}")
        for s in self.sources.sources:
            missing = set(s.topics) - topic_ids
            if missing:
                raise ValueError(f"источник {s.id}: неизвестные топики {sorted(missing)}")
        for stream, cfg in self.schedule.streams.items():
            for tid in cfg.topics:
                if tid not in topic_ids:
                    raise ValueError(f"поток {stream}: неизвестный топик {tid}")
                topic = next(t for t in self.topics.topics if t.id == tid)
                if topic.stream != stream:
                    raise ValueError(f"топик {tid} записан в поток {topic.stream}, а в расписании в {stream}")
        for day, tid in self.schedule.topic_rotation.items():
            if tid not in topic_ids:
                raise ValueError(f"ротация {day}: неизвестный топик {tid}")
        return self


def _yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_config(config_dir: Path = CONFIG_DIR) -> Config:
    return Config(
        topics=TopicsFile(**_yaml(config_dir / "topics.yaml")),
        sources=SourcesFile(**_yaml(config_dir / "sources.yaml")),
        schedule=Schedule(**_yaml(config_dir / "schedule.yaml")),
        glossary=_yaml(config_dir / "glossary.yaml"),
        anchors=_yaml(config_dir / "anchors.yaml").get("anchors", []),
        categories=_yaml(config_dir / "categories.yaml"),
        formats=_yaml(config_dir / "formats.yaml"),
        watchlist=_yaml(config_dir / "watchlist.yaml"),
        brand=(config_dir / "brand.md").read_text(encoding="utf-8"),
    )

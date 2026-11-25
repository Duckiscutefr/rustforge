"""Unified curriculum registry aggregating all 21 chapters and Appendices A-G."""

from __future__ import annotations

from rustforge.data.appendices import APPENDICES
from rustforge.data.chapters_01_07 import CHAPTERS_01_07
from rustforge.data.chapters_08_14 import CHAPTERS_08_14
from rustforge.data.chapters_15_21 import CHAPTERS_15_21
from rustforge.data.models import (
    AppendixSection,
    Chapter,
    ClozeDrill,
    CodingLab,
    CompilerClinic,
    FeynmanPrompt,
    RecallCard,
)

ALL_CHAPTERS: list[Chapter] = [*CHAPTERS_01_07, *CHAPTERS_08_14, *CHAPTERS_15_21]
CHAPTER_BY_NUM: dict[int, Chapter] = {ch.number: ch for ch in ALL_CHAPTERS}
APPENDIX_BY_CODE: dict[str, AppendixSection] = {ap.code.upper(): ap for ap in APPENDICES}


def get_chapter(number: int) -> Chapter | None:
    return CHAPTER_BY_NUM.get(number)


def all_recall_cards() -> list[RecallCard]:
    return [card for ch in ALL_CHAPTERS for card in ch.recall_cards]


def recall_card_by_id() -> dict[str, RecallCard]:
    return {card.id: card for card in all_recall_cards()}


def all_cloze_drills() -> list[ClozeDrill]:
    return [drill for ch in ALL_CHAPTERS for drill in ch.cloze_drills]


def all_clinics() -> list[CompilerClinic]:
    return [ch.clinic for ch in ALL_CHAPTERS]


def all_labs() -> list[CodingLab]:
    return [ch.lab for ch in ALL_CHAPTERS if ch.lab is not None]


__all__ = [
    "ALL_CHAPTERS",
    "APPENDICES",
    "APPENDIX_BY_CODE",
    "CHAPTER_BY_NUM",
    "AppendixSection",
    "Chapter",
    "ClozeDrill",
    "CodingLab",
    "CompilerClinic",
    "FeynmanPrompt",
    "RecallCard",
    "all_clinics",
    "all_cloze_drills",
    "all_labs",
    "all_recall_cards",
    "get_chapter",
    "recall_card_by_id",
]

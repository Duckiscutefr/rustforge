"""FSRS-inspired DSR (Difficulty, Stability, Retrievability) spaced repetition scheduler.

Implements the core DSR memory model (open-spaced-repetition FSRS):
- Difficulty (D): 1.0 (trivial) to 10.0 (hardest)
- Stability (S): days until recall probability R(t) decays to 90%
- Retrievability (R): R(t) = (1 + t / (9 * S))^(-1)
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


# Rating scale: 1=Again, 2=Hard, 3=Good, 4=Easy
RATING_LABELS = {
    1: "Again (forgot / wrong)",
    2: "Hard (recalled with heavy effort)",
    3: "Good (solid recall)",
    4: "Easy (instant recall)",
}

# Initial stability in days for a card's first rating (1..4)
INIT_STABILITY = {1: 0.4, 2: 1.2, 3: 3.0, 4: 7.5}
# Initial difficulty for first rating (1..4)
INIT_DIFFICULTY = {1: 7.2, 2: 6.0, 3: 4.8, 4: 3.2}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def retrievability(elapsed_days: float, stability: float) -> float:
    """Compute current recall probability R(t) using the FSRS power-law forgetting curve."""
    if stability <= 0:
        return 0.0
    if elapsed_days <= 0:
        return 1.0
    return (1.0 + elapsed_days / (9.0 * stability)) ** (-1.0)


def next_interval_days(stability: float, target_retention: float = 0.90) -> float:
    """Compute days until retrievability drops to target_retention."""
    r = max(0.70, min(0.97, target_retention))
    # Solve (1 + t / (9 * S))^(-1) = r  =>  t = 9 * S * (1/r - 1)
    days = 9.0 * stability * (1.0 / r - 1.0)
    return max(0.25, round(days, 2))


@dataclass
class CardState:
    card_id: str
    chapter: int
    difficulty: float = 5.0
    stability: float = 0.0
    reps: int = 0
    lapses: int = 0
    last_review: str | None = None
    due: str | None = None

    def elapsed_days(self, now: datetime | None = None) -> float:
        if not self.last_review:
            return 0.0
        now = now or utc_now()
        last = datetime.fromisoformat(self.last_review)
        return max(0.0, (now - last).total_seconds() / 86400.0)

    def current_retrievability(self, now: datetime | None = None) -> float:
        if self.reps == 0 or self.stability <= 0:
            return 0.0
        return retrievability(self.elapsed_days(now), self.stability)

    def is_due(self, now: datetime | None = None) -> bool:
        if not self.due:
            return True
        now = now or utc_now()
        return datetime.fromisoformat(self.due) <= now


def schedule_review(
    state: CardState,
    rating: int,
    target_retention: float = 0.90,
    now: datetime | None = None,
) -> tuple[CardState, float]:
    """Update a card's DSR state after a review rating (1..4) and return (new_state, interval_days)."""
    if rating not in (1, 2, 3, 4):
        raise ValueError(f"Rating must be 1, 2, 3, or 4; got {rating}")

    now = now or utc_now()
    if state.reps == 0 or state.stability <= 0:
        new_d = INIT_DIFFICULTY[rating]
        new_s = INIT_STABILITY[rating]
        new_lapses = state.lapses + (1 if rating == 1 else 0)
    else:
        elapsed = state.elapsed_days(now)
        r = retrievability(elapsed, state.stability)

        # Difficulty update with mean reversion toward neutral 5.0
        delta_d = -0.65 * (rating - 3)
        raw_d = state.difficulty + delta_d
        new_d = max(1.0, min(10.0, 0.90 * raw_d + 0.10 * 5.0))

        if rating == 1:
            # Lapse: stability drops sharply, difficulty rises
            new_lapses = state.lapses + 1
            new_s = max(0.4, round(state.stability * 0.25 * (1.0 + (10.0 - new_d) * 0.04), 3))
        else:
            new_lapses = state.lapses
            # Desirable difficulty bonus: lower R at review time yields larger stability gain
            hardness = {2: 0.78, 3: 1.0, 4: 1.32}[rating]
            gain = 1.0 + math.exp(0.55) * (11.0 - new_d) * (state.stability ** -0.18) * (
                math.exp(0.95 * (1.0 - r)) - 1.0
            ) * hardness
            new_s = round(max(state.stability + 0.2, state.stability * max(1.05, gain)), 3)

    interval = next_interval_days(new_s, target_retention=target_retention)
    if rating == 1:
        # Re-test lapses sooner (10 minutes in active sessions, ~0.25 days stored)
        interval = 0.25
    due_dt = now + timedelta(days=interval)

    updated = CardState(
        card_id=state.card_id,
        chapter=state.chapter,
        difficulty=round(new_d, 3),
        stability=round(new_s, 3),
        reps=state.reps + 1,
        lapses=new_lapses,
        last_review=now.isoformat(),
        due=due_dt.isoformat(),
    )
    return updated, interval


@dataclass
class UserSettings:
    bionic_reading: bool = False
    target_retention: float = 0.90
    sprint_minutes: int = 20


@dataclass
class ProgressStore:
    path: Path
    cards: dict[str, CardState] = field(default_factory=dict)
    completed_chapters: list[int] = field(default_factory=list)
    completed_labs: list[str] = field(default_factory=list)
    feynman_scores: dict[str, int] = field(default_factory=dict)
    total_reviews: int = 0
    total_correct: int = 0
    streak_days: int = 0
    last_active_date: str | None = None
    settings: UserSettings = field(default_factory=UserSettings)

    @classmethod
    def default_path(cls) -> Path:
        return Path.home() / ".rustforge" / "progress.json"

    @classmethod
    def load(cls, path: Path | None = None) -> "ProgressStore":
        target = path or cls.default_path()
        if not target.exists():
            return cls(path=target)
        try:
            raw: dict[str, Any] = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls(path=target)

        cards = {
            cid: CardState(**cdata)
            for cid, cdata in raw.get("cards", {}).items()
            if isinstance(cdata, dict)
        }
        settings_raw = raw.get("settings", {})
        settings = UserSettings(
            bionic_reading=bool(settings_raw.get("bionic_reading", False)),
            target_retention=float(settings_raw.get("target_retention", 0.90)),
            sprint_minutes=int(settings_raw.get("sprint_minutes", 20)),
        )
        return cls(
            path=target,
            cards=cards,
            completed_chapters=list(raw.get("completed_chapters", [])),
            completed_labs=list(raw.get("completed_labs", [])),
            feynman_scores=dict(raw.get("feynman_scores", {})),
            total_reviews=int(raw.get("total_reviews", 0)),
            total_correct=int(raw.get("total_correct", 0)),
            streak_days=int(raw.get("streak_days", 0)),
            last_active_date=raw.get("last_active_date"),
            settings=settings,
        )

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "cards": {cid: asdict(card) for cid, card in self.cards.items()},
            "completed_chapters": sorted(set(self.completed_chapters)),
            "completed_labs": sorted(set(self.completed_labs)),
            "feynman_scores": self.feynman_scores,
            "total_reviews": self.total_reviews,
            "total_correct": self.total_correct,
            "streak_days": self.streak_days,
            "last_active_date": self.last_active_date,
            "settings": asdict(self.settings),
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def touch_streak(self, today: datetime | None = None) -> None:
        today_str = (today or utc_now()).date().isoformat()
        if self.last_active_date == today_str:
            return
        if self.last_active_date:
            prev = datetime.fromisoformat(self.last_active_date).date()
            curr = datetime.fromisoformat(today_str).date()
            if (curr - prev).days == 1:
                self.streak_days += 1
            else:
                self.streak_days = 1
        else:
            self.streak_days = 1
        self.last_active_date = today_str

    def record_review(self, card_id: str, chapter: int, rating: int, now: datetime | None = None) -> tuple[CardState, float]:
        current = self.cards.get(card_id, CardState(card_id=card_id, chapter=chapter))
        updated, interval = schedule_review(
            current,
            rating=rating,
            target_retention=self.settings.target_retention,
            now=now,
        )
        self.cards[card_id] = updated
        self.total_reviews += 1
        if rating >= 3:
            self.total_correct += 1
        self.touch_streak(now)
        self.save()
        return updated, interval

    def mark_chapter_read(self, chapter: int, now: datetime | None = None) -> None:
        if chapter not in self.completed_chapters:
            self.completed_chapters.append(chapter)
        self.touch_streak(now)
        self.save()

    def mark_lab_passed(self, lab_id: str, now: datetime | None = None) -> None:
        if lab_id not in self.completed_labs:
            self.completed_labs.append(lab_id)
        self.touch_streak(now)
        self.save()

    def record_feynman(self, chapter: int, score_pct: int, now: datetime | None = None) -> None:
        key = str(chapter)
        self.feynman_scores[key] = max(score_pct, self.feynman_scores.get(key, 0))
        self.touch_streak(now)
        self.save()

    def due_cards(self, all_card_ids: list[tuple[str, int]], now: datetime | None = None) -> list[tuple[str, int, CardState]]:
        """Return cards that are due for review, prioritized by lowest retrievability."""
        now = now or utc_now()
        due: list[tuple[float, str, int, CardState]] = []
        for cid, ch in all_card_ids:
            if cid in self.cards:
                st = self.cards[cid]
                if st.is_due(now):
                    due.append((st.current_retrievability(now), cid, ch, st))
        due.sort(key=lambda item: item[0])
        return [(cid, ch, st) for _, cid, ch, st in due]

    def chapter_mastery(self, chapter: int, chapter_card_ids: list[str], now: datetime | None = None) -> float:
        """Estimate mastery (0.0 to 1.0) for a chapter based on card retrievability and stability."""
        if not chapter_card_ids:
            return 1.0 if chapter in self.completed_chapters else 0.0
        now = now or utc_now()
        scores: list[float] = []
        for cid in chapter_card_ids:
            st = self.cards.get(cid)
            if not st or st.reps == 0:
                scores.append(0.0)
            else:
                r = st.current_retrievability(now)
                stability_factor = min(1.0, math.log1p(st.stability) / math.log1p(21.0))
                scores.append(0.6 * r + 0.4 * stability_factor)
        base = sum(scores) / len(scores)
        if chapter in self.completed_chapters:
            base = min(1.0, base + 0.10)
        return round(base, 3)

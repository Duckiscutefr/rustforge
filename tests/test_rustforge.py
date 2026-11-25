"""Automated test suite for RustForge CLI."""

from __future__ import annotations

import io
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from rustforge.cli import main
from rustforge.data import (
    ALL_CHAPTERS,
    APPENDICES,
    all_clinics,
    all_cloze_drills,
    all_labs,
    all_recall_cards,
    get_chapter,
)
from rustforge.fsrs import CardState, ProgressStore, next_interval_days, retrievability, schedule_review
from rustforge.ui import Ansi, TerminalUI


class TestCurriculumIntegrity(unittest.TestCase):
    def test_all_21_chapters_present_and_ordered(self) -> None:
        self.assertEqual([c.number for c in ALL_CHAPTERS], list(range(1, 22)))
        for num in range(1, 22):
            ch = get_chapter(num)
            self.assertIsNotNone(ch)
            assert ch is not None
            self.assertTrue(ch.mental_model.strip())
            self.assertTrue(ch.diagram.strip())
            self.assertGreaterEqual(len(ch.key_rules), 3)
            self.assertGreaterEqual(len(ch.recall_cards), 2)
            self.assertGreaterEqual(len(ch.cloze_drills), 1)
            self.assertTrue(ch.feynman.rubric_points)
            self.assertTrue(ch.feynman.key_terms)

    def test_all_7_appendices_present(self) -> None:
        self.assertEqual([a.code for a in APPENDICES], ["A", "B", "C", "D", "E", "F", "G"])

    def test_unique_ids_and_valid_answer_indices(self) -> None:
        card_ids = [c.id for c in all_recall_cards()]
        self.assertEqual(len(card_ids), len(set(card_ids)))
        for card in all_recall_cards():
            self.assertIn(card.answer_index, range(len(card.options)))

        cloze_ids = [d.id for d in all_cloze_drills()]
        self.assertEqual(len(cloze_ids), len(set(cloze_ids)))
        for drill in all_cloze_drills():
            self.assertIn("___", drill.code_template)
            self.assertTrue(drill.accepted_answers)

        for clinic in all_clinics():
            self.assertIn(clinic.answer_index, range(len(clinic.options)))

        self.assertGreaterEqual(len(all_labs()), 10)

    def test_zero_emojis_in_curriculum(self) -> None:
        emoji_re = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]")
        for ch in ALL_CHAPTERS:
            blob = " ".join([ch.title, ch.summary, ch.mental_model, ch.diagram, *ch.key_rules])
            self.assertIsNone(emoji_re.search(blob), f"Emoji found in Ch {ch.number}")


class TestFSRSEngine(unittest.TestCase):
    def test_retrievability_decays_monotonically(self) -> None:
        r0 = retrievability(0.0, 5.0)
        r5 = retrievability(5.0, 5.0)
        r20 = retrievability(20.0, 5.0)
        self.assertEqual(r0, 1.0)
        self.assertAlmostEqual(r5, 0.9, places=4)
        self.assertGreater(r5, r20)
        self.assertGreater(r20, 0.0)

    def test_schedule_review_growth_and_lapse(self) -> None:
        t0 = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)
        card = CardState(card_id="ch04_c1", chapter=4)

        # First review: Good (3)
        c1, iv1 = schedule_review(card, rating=3, now=t0)
        self.assertEqual(c1.reps, 1)
        self.assertGreater(c1.stability, 0.0)
        self.assertGreaterEqual(iv1, 1.0)

        # Second review after interval: Easy (4) should grow stability & reduce difficulty
        t1 = t0 + timedelta(days=iv1)
        c2, iv2 = schedule_review(c1, rating=4, now=t1)
        self.assertGreater(c2.stability, c1.stability)
        self.assertLess(c2.difficulty, c1.difficulty)
        self.assertGreater(iv2, iv1)

        # Lapse: Again (1) should cut stability sharply and increment lapses
        t2 = t1 + timedelta(days=iv2)
        c3, iv3 = schedule_review(c2, rating=1, now=t2)
        self.assertEqual(c3.lapses, 1)
        self.assertLess(c3.stability, c2.stability)
        self.assertEqual(iv3, 0.25)

    def test_next_interval_matches_target_retention(self) -> None:
        s = 10.0
        iv = next_interval_days(s, target_retention=0.90)
        self.assertAlmostEqual(iv, 10.0, places=2)

    def test_progress_store_persistence_and_streak(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "progress.json"
            store = ProgressStore.load(path)
            t1 = datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc)
            t2 = datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc)

            store.record_review("ch04_c1", chapter=4, rating=3, now=t1)
            store.record_review("ch04_c2", chapter=4, rating=4, now=t2)
            store.mark_chapter_read(4, now=t2)
            store.mark_lab_passed("lab_ch04_slice", now=t2)
            store.record_feynman(4, 92, now=t2)

            reloaded = ProgressStore.load(path)
            self.assertEqual(reloaded.streak_days, 2)
            self.assertEqual(reloaded.total_reviews, 2)
            self.assertIn(4, reloaded.completed_chapters)
            self.assertIn("lab_ch04_slice", reloaded.completed_labs)
            self.assertEqual(reloaded.feynman_scores["4"], 92)
            self.assertGreater(reloaded.chapter_mastery(4, ["ch04_c1", "ch04_c2"], now=t2), 0.5)


class TestTerminalUI(unittest.TestCase):
    def test_bionic_preserves_inline_code(self) -> None:
        ui = TerminalUI(use_color=True, bionic=True, width=80)
        # Force ANSI enabled for unit test even when stdout is not a TTY
        ui.use_color = True
        formatted = ui.format_prose("Use `let mut x` for ownership")
        # Inline code must stay verbatim without ANSI bold inserted inside its letters
        self.assertIn("`let mut x`", formatted)
        # Prose word "ownership" should contain BOLD prefix
        self.assertIn(Ansi.BOLD, formatted)


class TestCLISmokeFlows(unittest.TestCase):
    def test_map_and_reference_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_file = str(Path(tmp) / "progress.json")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--no-color", "--data-file", data_file, "map"])
            self.assertEqual(rc, 0)
            out = buf.getvalue()
            self.assertIn("Ch 01", out)
            self.assertIn("Ch 21", out)

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(["--no-color", "--data-file", data_file, "ref", "E"])
            self.assertEqual(rc2, 0)
            self.assertIn("2024", buf2.getvalue())

    def test_interactive_learn_and_feynman_flows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_file = str(Path(tmp) / "progress.json")
            # Simulate: Enter to start drills -> choose 2 -> rate 3 -> choose 2 -> rate 3 -> cloze `&str` -> clinic 1
            inputs = iter(["", "2", "3", "2", "3", "&str", "1"])
            buf = io.StringIO()
            with patch("builtins.input", side_effect=lambda _: next(inputs)), redirect_stdout(buf):
                rc = main(["--no-color", "--data-file", data_file, "learn", "4"])
            self.assertEqual(rc, 0)
            self.assertIn("CHAPTER 04 COMPLETE", buf.getvalue())

            # Feynman flow on Chapter 4
            feyn_inputs = iter(["Mutable and immutable borrows prevent data races and dangling pointers.", "95"])
            buf2 = io.StringIO()
            with patch("builtins.input", side_effect=lambda _: next(feyn_inputs)), redirect_stdout(buf2):
                rc2 = main(["--no-color", "--data-file", data_file, "feynman", "4"])
            self.assertEqual(rc2, 0)
            self.assertIn("Saved Feynman mastery score", buf2.getvalue())


if __name__ == "__main__":
    unittest.main()

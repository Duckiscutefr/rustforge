"""Interactive neuroscience-backed learning engine for RustForge."""

from __future__ import annotations

import os
import random
import subprocess
import time
from typing import Sequence

from rustforge.data import (
    ALL_CHAPTERS,
    APPENDICES,
    APPENDIX_BY_CODE,
    Chapter,
    ClozeDrill,
    CodingLab,
    CompilerClinic,
    RecallCard,
    all_clinics,
    all_cloze_drills,
    all_labs,
    all_recall_cards,
    get_chapter,
    recall_card_by_id,
)
from rustforge.fsrs import RATING_LABELS, ProgressStore
from rustforge.runner import compile_and_test_rust, lab_workspace_file, rustc_version
from rustforge.ui import TerminalUI


class LearningEngine:
    """Executes all RustForge study, recall, debugging, Feynman, lab, and sprint flows."""

    def __init__(self, ui: TerminalUI, store: ProgressStore) -> None:
        self.ui = ui
        self.store = store

    # ------------------------------------------------------------------
    # Core primitive drills
    # ------------------------------------------------------------------
    def _ask_choice(self, options: Sequence[str]) -> int | None:
        """Display numbered options (1..N) and return 0-based choice, or None on quit."""
        print()
        for idx, opt in enumerate(options, start=1):
            print(f"  [{idx}] {self.ui.format_prose(opt)}")
        while True:
            raw = self.ui.prompt(f"Predict answer (1-{len(options)}, or 'q' to quit)")
            if raw.lower() == "q":
                return None
            if raw.isdigit():
                val = int(raw)
                if 1 <= val <= len(options):
                    return val - 1
            print(self.ui.dim(f"  Enter a number from 1 to {len(options)} (or 'q')."))

    def run_recall_card(self, card: RecallCard, schedule: bool = True) -> bool | None:
        """Run a prediction-before-reveal recall card. Returns True/False, or None if quit."""
        self.ui.section(f"Active Recall  |  Ch {card.chapter:02d}  |  {card.id}")
        self.ui.paragraph(card.prompt)
        print()
        self.ui.code_block(card.code, title="PREDICT BEFORE REVEAL")

        choice = self._ask_choice(card.options)
        if choice is None:
            return None

        correct = choice == card.answer_index
        if correct:
            self.ui.callout("CORRECT", card.explanation)
        else:
            expected = card.options[card.answer_index]
            self.ui.callout(
                "HYPERCORRECTION (MISCONCEPTION CAUGHT)",
                f"Correct answer: [{card.answer_index + 1}] {expected}\n\n{card.explanation}",
            )

        if schedule:
            default_rating = "3" if correct else "1"
            print()
            for r_num, label in RATING_LABELS.items():
                print(f"  ({r_num}) {label}")
            while True:
                raw = self.ui.prompt("Rate recall effort (1-4)", default=default_rating)
                if raw.lower() == "q":
                    return None
                if raw in ("1", "2", "3", "4"):
                    rating = int(raw)
                    break
                print(self.ui.dim("  Enter 1, 2, 3, or 4."))
            updated, interval = self.store.record_review(card.id, card.chapter, rating)
            print(
                self.ui.dim(
                    f"  FSRS updated -> D={updated.difficulty:.2f}  S={updated.stability:.2f}d  "
                    f"Next review in {interval:.2f} day(s)."
                )
            )
        return correct

    def run_cloze_drill(self, drill: ClozeDrill) -> bool | None:
        """Run a generation-effect fill-in-the-blank syntax drill."""
        self.ui.section(f"Generation Drill  |  Ch {drill.chapter:02d}  |  {drill.id}")
        self.ui.paragraph(drill.prompt)
        print()
        self.ui.code_block(drill.code_template, title="FILL IN `___`")

        raw = self.ui.prompt("Type exact Rust syntax for `___` (or '?' for hint, 'q' to quit)")
        if raw.lower() == "q":
            return None
        if raw == "?":
            print(self.ui.dim(f"  Hint: {drill.hint}"))
            raw = self.ui.prompt("Type exact Rust syntax for `___` (or 'q' to quit)")
            if raw.lower() == "q":
                return None

        normalized = "".join(raw.split())
        accepted = {"".join(ans.split()) for ans in drill.accepted_answers}
        if normalized in accepted:
            self.ui.callout("GENERATED CORRECTLY", drill.explanation)
            return True
        self.ui.callout(
            "CHECK SYNTAX",
            f"Expected: `{drill.accepted_answers[0]}`\n\n{drill.explanation}",
        )
        return False

    def run_clinic_item(self, clinic: CompilerClinic) -> bool | None:
        """Run a single rustc compiler-error diagnostic clinic."""
        self.ui.section(f"Compiler Clinic [{clinic.error_code}]  |  Ch {clinic.chapter:02d}: {clinic.title}")
        self.ui.code_block(clinic.broken_code, title="BROKEN RUST")
        print()
        self.ui.code_block(clinic.compiler_output, title=f"RUSTC {clinic.error_code}")
        print()
        self.ui.paragraph(clinic.question)

        choice = self._ask_choice(clinic.options)
        if choice is None:
            return None

        correct = choice == clinic.answer_index
        label = "DIAGNOSIS CORRECT" if correct else "DIAGNOSIS MISSED"
        expected = clinic.options[clinic.answer_index]
        self.ui.callout(label, f"Answer: [{clinic.answer_index + 1}] {expected}\n\n{clinic.mental_model}")
        print()
        self.ui.code_block(clinic.fix_code, title="FIXED RUST")
        return correct

    # ------------------------------------------------------------------
    # Top-level study modes
    # ------------------------------------------------------------------
    def run_learn(self, chapter_num: int) -> None:
        ch = get_chapter(chapter_num)
        if not ch:
            print(f"Chapter {chapter_num} not found. Valid chapters: 1 to 21.")
            return

        self.ui.banner(f"Chapter {ch.number:02d}: {ch.title}", ch.summary)
        self.ui.section("Core Mental Model")
        self.ui.paragraph(ch.mental_model)

        self.ui.section("Dual-Coded Visual Model")
        self.ui.diagram(ch.diagram, title=ch.diagram_title)

        self.ui.section("Key Rules (Rust 2024 Edition)")
        self.ui.bullets(ch.key_rules)

        if not self.ui.pause("Press Enter to start Active Recall drills (or 'q' to finish reading)"):
            self.store.mark_chapter_read(ch.number)
            return

        for card in ch.recall_cards:
            res = self.run_recall_card(card, schedule=True)
            if res is None:
                self.store.mark_chapter_read(ch.number)
                return

        for drill in ch.cloze_drills:
            res = self.run_cloze_drill(drill)
            if res is None:
                self.store.mark_chapter_read(ch.number)
                return

        res = self.run_clinic_item(ch.clinic)
        if res is None:
            self.store.mark_chapter_read(ch.number)
            return

        self.store.mark_chapter_read(ch.number)
        self.ui.callout(
            f"CHAPTER {ch.number:02d} COMPLETE",
            "Chapter logged. Cards are now scheduled in your FSRS spaced-repetition queue.",
        )

    def run_review(self, limit: int = 10) -> None:
        cards = all_recall_cards()
        by_id = recall_card_by_id()
        due = self.store.due_cards([(c.id, c.chapter) for c in cards])

        queue: list[RecallCard] = [by_id[cid] for cid, _, _ in due[:limit]]
        mode_note = f"{len(due)} card(s) due in FSRS queue"

        if not queue:
            unseen = [c for c in cards if c.id not in self.store.cards]
            if not unseen:
                self.ui.banner("FSRS Review Queue", "All scheduled cards are fresh! Run `interleave` for extra practice.")
                return
            queue = unseen[:limit]
            mode_note = f"0 due -> introducing {len(queue)} new unseen card(s)"

        self.ui.banner("FSRS Spaced Repetition Review", mode_note)
        done = 0
        correct = 0
        for card in queue:
            res = self.run_recall_card(card, schedule=True)
            if res is None:
                break
            done += 1
            if res:
                correct += 1

        if done > 0:
            pct = int(round(100 * correct / done))
            self.ui.callout("REVIEW SUMMARY", f"Completed {done} card(s) | Accuracy: {correct}/{done} ({pct}%).")

    def run_interleave(self, count: int = 8) -> None:
        """Mix recall cards, cloze drills, and compiler clinics across distinct chapters."""
        self.ui.banner(
            "Interleaved Desirable-Difficulty Session",
            "Mixing concepts across chapters forces discrimination instead of autopilot recall.",
        )
        pool: list[tuple[str, int, object]] = []
        for c in all_recall_cards():
            pool.append(("recall", c.chapter, c))
        for d in all_cloze_drills():
            pool.append(("cloze", d.chapter, d))
        for cl in all_clinics():
            pool.append(("clinic", cl.chapter, cl))

        random.shuffle(pool)
        selected: list[tuple[str, int, object]] = []
        last_ch = -1
        for item in pool:
            if len(selected) >= count:
                break
            if item[1] != last_ch:
                selected.append(item)
                last_ch = item[1]

        done = 0
        correct = 0
        for kind, _, obj in selected:
            if kind == "recall":
                res = self.run_recall_card(obj, schedule=True)  # type: ignore[arg-type]
            elif kind == "cloze":
                res = self.run_cloze_drill(obj)  # type: ignore[arg-type]
            else:
                res = self.run_clinic_item(obj)  # type: ignore[arg-type]
            if res is None:
                break
            done += 1
            if res:
                correct += 1

        if done > 0:
            pct = int(round(100 * correct / done))
            self.ui.callout("INTERLEAVE COMPLETE", f"Drills: {done} | Accuracy: {correct}/{done} ({pct}%).")

    def run_debug(self, chapter_num: int | None = None) -> None:
        clinics = [get_chapter(chapter_num).clinic] if chapter_num and get_chapter(chapter_num) else list(all_clinics())
        if chapter_num is None:
            random.shuffle(clinics)
            clinics = clinics[:6]
        self.ui.banner("Borrow Checker & Compiler Error Clinic", "Diagnose real rustc errors before seeing the fix.")
        done = 0
        correct = 0
        for clinic in clinics:
            res = self.run_clinic_item(clinic)
            if res is None:
                break
            done += 1
            if res:
                correct += 1
        if done > 0:
            self.ui.callout("CLINIC SUMMARY", f"Diagnosed {correct}/{done} compiler errors accurately.")

    def run_feynman(self, chapter_num: int | None = None) -> None:
        if chapter_num is None:
            ch = random.choice(ALL_CHAPTERS)
        else:
            ch = get_chapter(chapter_num)
            if not ch:
                print(f"Chapter {chapter_num} not found. Valid: 1..21.")
                return

        fp = ch.feynman
        self.ui.banner(f"Feynman Self-Explanation  |  Chapter {ch.number:02d}", ch.title)
        self.ui.paragraph(fp.question)
        print()
        print(self.ui.dim("  Write your explanation in plain English (one paragraph). Press Enter to submit:"))
        answer = self.ui.prompt("Your explanation (or 'q' to cancel)")
        if answer.lower() == "q":
            return

        lower = answer.lower()
        hits = [term for term in fp.key_terms if term.lower() in lower]
        auto_pct = int(round(100 * len(hits) / max(1, len(fp.key_terms))))

        self.ui.section("Rubric Checklist (Compare Your Explanation)")
        self.ui.bullets(fp.rubric_points)
        self.ui.callout("MODEL EXPLANATION", fp.model_answer)
        print()
        print(
            self.ui.dim(
                f"  Key concepts detected ({len(hits)}/{len(fp.key_terms)}): "
                + (", ".join(hits) if hits else "none detected")
                + f"  [auto estimate: {auto_pct}%]"
            )
        )
        raw_score = self.ui.prompt("Self-grade your explanation (0-100)", default=str(auto_pct))
        try:
            score = max(0, min(100, int(raw_score)))
        except ValueError:
            score = auto_pct
        self.store.record_feynman(ch.number, score)
        print(self.ui.dim(f"  Saved Feynman mastery score for Ch {ch.number:02d}: {score}%."))

    def run_lab(self, chapter_num: int | None = None) -> None:
        labs = all_labs()
        ver = rustc_version()
        self.ui.banner(
            "Live Rust 2024 Coding Labs",
            f"Toolchain: {ver}" if ver else "Toolchain: rustc not detected (offline guided mode active)",
        )

        selected_lab: CodingLab | None = None
        if chapter_num is not None:
            for lab in labs:
                if lab.chapter == chapter_num:
                    selected_lab = lab
                    break
            if not selected_lab:
                print(f"No coding lab for Chapter {chapter_num}. Available lab chapters: {[l.chapter for l in labs]}")
                return
        else:
            for lab in labs:
                status = "[PASS]" if lab.id in self.store.completed_labs else "[OPEN]"
                print(f"  {status} Ch {lab.chapter:02d}  {lab.title}")
            raw = self.ui.prompt("Enter chapter number to open lab (or 'q' to return)")
            if raw.lower() == "q" or not raw.isdigit():
                return
            for lab in labs:
                if lab.chapter == int(raw):
                    selected_lab = lab
                    break
            if not selected_lab:
                print("No lab for that chapter.")
                return

        self._execute_lab(selected_lab, has_rustc=ver is not None)

    def _execute_lab(self, lab: CodingLab, has_rustc: bool) -> None:
        self.ui.section(f"Lab Ch {lab.chapter:02d}: {lab.title}")
        self.ui.paragraph(lab.objective)
        print()
        self.ui.code_block(lab.starter_code, title="STARTER CODE")

        path = lab_workspace_file(lab.id, lab.starter_code)
        print(self.ui.dim(f"\n  Lab file ready at: {path}"))

        while True:
            print()
            if has_rustc:
                print("  [e] Edit file in $EDITOR   [t] Compile & run tests   [s] Show solution   [r] Reset file   [q] Back")
            else:
                print("  [s] Show reference solution   [r] Reset starter file   [q] Back")
                print(self.ui.dim("  (Install rustc via https://rustup.rs/ to enable live compilation & tests.)"))
            cmd = self.ui.prompt("Lab action").lower()
            if cmd == "q":
                return
            if cmd == "s":
                self.ui.code_block(lab.solution_code, title="REFERENCE SOLUTION")
            elif cmd == "r":
                path.write_text(lab.starter_code.strip() + "\n", encoding="utf-8")
                print(self.ui.dim("  Reset lab file to starter code."))
            elif cmd == "e" and has_rustc:
                editor = os.environ.get("EDITOR") or os.environ.get("VISUAL") or "nano"
                try:
                    subprocess.run([editor, str(path)], check=False)
                except OSError:
                    print(self.ui.dim(f"  Could not launch editor `{editor}`. Edit {path} directly."))
            elif cmd == "t" and has_rustc:
                source = path.read_text(encoding="utf-8")
                res = compile_and_test_rust(source, edition="2024")
                if res.passed:
                    self.store.mark_lab_passed(lab.id)
                    self.ui.callout("ALL TESTS PASSED", f"Compiled with Rust Edition {res.edition_used}.\n\n{res.stdout.strip()}")
                elif res.compiled:
                    self.ui.callout("TESTS FAILED", (res.stdout + "\n" + res.stderr).strip())
                else:
                    self.ui.callout("COMPILE ERROR", res.stderr.strip())

    def run_sprint(self, minutes: int | None = None) -> None:
        """Timed 15-25 min focus sprint combining FSRS, interleaving, debugging, and Feynman."""
        target_min = minutes or self.store.settings.sprint_minutes
        start = time.monotonic()
        deadline = start + target_min * 60

        self.ui.banner(
            f"{target_min}-Minute Neuroscience Mastery Sprint",
            "Flow: FSRS Due Recall -> Interleaved Drills -> Compiler Clinic -> Feynman Check",
        )

        stats = {"done": 0, "correct": 0, "chapters": set()}
        cards = all_recall_cards()
        by_id = recall_card_by_id()
        due = self.store.due_cards([(c.id, c.chapter) for c in cards])

        # Stage 1: Up to 3 due (or new) FSRS cards
        stage1 = [by_id[cid] for cid, _, _ in due[:3]]
        if len(stage1) < 3:
            seen = {c.id for c in stage1}
            extras = [c for c in cards if c.id not in self.store.cards and c.id not in seen]
            stage1.extend(extras[: 3 - len(stage1)])

        for card in stage1:
            if time.monotonic() >= deadline:
                break
            res = self.run_recall_card(card, schedule=True)
            if res is None:
                self._sprint_peak_end(start, stats)
                return
            stats["done"] += 1
            stats["chapters"].add(card.chapter)
            if res:
                stats["correct"] += 1

        # Stage 2: 2 Generation cloze drills
        drills = list(all_cloze_drills())
        random.shuffle(drills)
        for drill in drills[:2]:
            if time.monotonic() >= deadline:
                break
            res = self.run_cloze_drill(drill)
            if res is None:
                self._sprint_peak_end(start, stats)
                return
            stats["done"] += 1
            stats["chapters"].add(drill.chapter)
            if res:
                stats["correct"] += 1

        # Stage 3: 1 Compiler Error Clinic
        if time.monotonic() < deadline:
            clinic = random.choice(all_clinics())
            res = self.run_clinic_item(clinic)
            if res is None:
                self._sprint_peak_end(start, stats)
                return
            stats["done"] += 1
            stats["chapters"].add(clinic.chapter)
            if res:
                stats["correct"] += 1

        # Stage 4: 1 Feynman Self-Explanation
        if time.monotonic() < deadline:
            self.run_feynman()

        self._sprint_peak_end(start, stats)

    def _sprint_peak_end(self, start: float, stats: dict) -> None:
        elapsed_sec = int(time.monotonic() - start)
        mins, secs = divmod(elapsed_sec, 60)
        done = stats["done"]
        correct = stats["correct"]
        pct = int(round(100 * correct / done)) if done else 0

        # Identify lowest-mastery chapter to recommend next
        weakest = min(
            ALL_CHAPTERS,
            key=lambda ch: self.store.chapter_mastery(ch.number, [c.id for c in ch.recall_cards]),
        )
        self.ui.callout(
            "PEAK-END SPRINT RECAP",
            f"Duration: {mins}m {secs:02d}s  |  Drills: {done}  |  Accuracy: {pct}%  |  Streak: {self.store.streak_days} day(s)\n"
            f"Recommended next focus -> Chapter {weakest.number:02d}: {weakest.title}",
        )

    def run_map(self) -> None:
        self.ui.banner("Rust 2024 Mastery Radar (21 Chapters + Appendices A-G)")
        all_cards = all_recall_cards()
        due_count = len(self.store.due_cards([(c.id, c.chapter) for c in all_cards]))
        ver = rustc_version() or "not installed (offline mode)"
        bionic_label = "ON" if self.ui.bionic else "OFF"

        print(
            f"  Streak: {self.store.streak_days}d  |  Reviews: {self.store.total_reviews}  |  "
            f"Due Now: {due_count}  |  Labs: {len(self.store.completed_labs)}/{len(all_labs())}"
        )
        print(f"  Bionic Reading: {bionic_label}  |  Target Retention: {int(self.store.settings.target_retention * 100)}%  |  rustc: {ver}")
        print(self.ui.hr("-"))

        for ch in ALL_CHAPTERS:
            mastery = self.store.chapter_mastery(ch.number, [c.id for c in ch.recall_cards])
            bar = self.ui.progress_bar(mastery, width=16)
            read_mark = "R" if ch.number in self.store.completed_chapters else "."
            feyn_mark = "F" if str(ch.number) in self.store.feynman_scores else "."
            lab_mark = "L" if (ch.lab and ch.lab.id in self.store.completed_labs) else ("." if ch.lab else "-")
            print(f"  Ch {ch.number:02d} {bar} [{read_mark}{feyn_mark}{lab_mark}] {ch.title[:44]}")

        print(self.ui.hr("-"))
        print(self.ui.dim("  Flags: [R]=Chapter Read  [F]=Feynman Done  [L]=Lab Passed  [-]=No Lab"))

    def run_reference(self, code: str | None = None) -> None:
        if code:
            ap = APPENDIX_BY_CODE.get(code.upper())
            if not ap:
                print(f"Unknown appendix '{code}'. Valid: A, B, C, D, E, F, G.")
                return
            self._show_appendix(ap)
            return

        self.ui.banner("Rust 2024 Appendices A-G Quick Reference")
        for ap in APPENDICES:
            print(f"  [{ap.code}] {ap.title} -- {ap.summary}")
        raw = self.ui.prompt("Enter appendix letter (A-G, or 'q' to return)")
        if raw.lower() == "q":
            return
        ap = APPENDIX_BY_CODE.get(raw.upper())
        if ap:
            self._show_appendix(ap)
        else:
            print("Invalid appendix code.")

    def _show_appendix(self, ap) -> None:
        self.ui.banner(f"Appendix {ap.code}: {ap.title}", ap.summary)
        for key, desc in ap.entries:
            print(f"  {self.ui.bold(key)}")
            self.ui.paragraph(desc, indent=4)
        if ap.notes:
            self.ui.section("Rust 2024 Notes")
            self.ui.bullets(ap.notes)

    def run_settings(self) -> None:
        while True:
            self.ui.banner("RustForge Settings & Cognitive Protocol")
            bionic = "ON" if self.store.settings.bionic_reading else "OFF"
            print(f"  [1] Bionic Reading (prose fixation anchors): {bionic}")
            print(f"  [2] Target FSRS Retention:                   {int(self.store.settings.target_retention * 100)}%")
            print(f"  [3] Default Sprint Duration:                 {self.store.settings.sprint_minutes} min")
            print("  [q] Back")
            cmd = self.ui.prompt("Choose setting")
            if cmd.lower() == "q":
                return
            if cmd == "1":
                self.store.settings.bionic_reading = not self.store.settings.bionic_reading
                self.ui.bionic = self.store.settings.bionic_reading
                self.store.save()
                print(self.ui.dim(f"  Bionic Reading set to {'ON' if self.ui.bionic else 'OFF'}."))
            elif cmd == "2":
                raw = self.ui.prompt("Enter target retention (80-95)", default="90")
                if raw.isdigit() and 80 <= int(raw) <= 95:
                    self.store.settings.target_retention = int(raw) / 100.0
                    self.store.save()
            elif cmd == "3":
                raw = self.ui.prompt("Enter sprint length in minutes (10-45)", default="20")
                if raw.isdigit() and 10 <= int(raw) <= 45:
                    self.store.settings.sprint_minutes = int(raw)
                    self.store.save()

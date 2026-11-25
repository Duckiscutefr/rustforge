"""Command-line interface and interactive dashboard for RustForge."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rustforge import __edition__, __version__
from rustforge.engine import LearningEngine
from rustforge.fsrs import ProgressStore
from rustforge.ui import TerminalUI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rustforge",
        description="Neuroscience-backed terminal mastery trainer for Rust (2024 Edition, Ch 1-21 + Appendices A-G).",
    )
    parser.add_argument("--version", action="version", version=f"rustforge {__version__} (Rust {__edition__} Edition)")
    parser.add_argument("--bionic", action="store_true", help="Enable Bionic Reading fixation anchors for prose")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI terminal styling")
    parser.add_argument("--data-file", type=Path, default=None, help="Custom path for progress JSON storage")

    sub = parser.add_subparsers(dest="command")

    p_learn = sub.add_parser("learn", help="Study a chapter (1-21) with mental models, diagrams, and drills")
    p_learn.add_argument("chapter", type=int, help="Chapter number (1..21)")

    p_review = sub.add_parser("review", help="Run FSRS spaced-repetition due review queue")
    p_review.add_argument("-n", "--limit", type=int, default=10, help="Max cards per session (default: 10)")

    p_inter = sub.add_parser("interleave", help="Cross-chapter desirable-difficulty drill mixer")
    p_inter.add_argument("-n", "--count", type=int, default=8, help="Number of mixed drills (default: 8)")

    p_debug = sub.add_parser("debug", help="Borrow-checker & rustc compiler-error diagnostic clinic")
    p_debug.add_argument("chapter", type=int, nargs="?", default=None, help="Optional chapter number (1..21)")

    p_feyn = sub.add_parser("feynman", help="Feynman self-explanation trainer with rubric")
    p_feyn.add_argument("chapter", type=int, nargs="?", default=None, help="Optional chapter number (1..21)")

    p_lab = sub.add_parser("lab", help="Live rustc coding labs (Edition 2024)")
    p_lab.add_argument("chapter", type=int, nargs="?", default=None, help="Optional chapter number")

    p_sprint = sub.add_parser("sprint", help="Timed 15-25 min focus sprint with Peak-End recap")
    p_sprint.add_argument("-m", "--minutes", type=int, default=None, help="Sprint duration in minutes")

    sub.add_parser("map", help="Show mastery radar across all 21 chapters")

    p_ref = sub.add_parser("ref", help="Quick reference for Appendices A-G")
    p_ref.add_argument("appendix", nargs="?", default=None, help="Appendix letter (A..G)")

    sub.add_parser("settings", help="Configure Bionic Reading, retention target, and sprint length")
    return parser


def interactive_loop(engine: LearningEngine) -> int:
    while True:
        engine.ui.banner(
            f"RUSTFORGE v{__version__}  //  RUST {__edition__} EDITION MASTERY CLI",
            "FSRS Spaced Repetition | Active Recall | Compiler Clinic | Feynman | Live rustc Labs",
        )
        print("  [1] map         Mastery radar (all 21 chapters)")
        print("  [2] sprint      Timed focus sprint (FSRS + Interleave + Clinic + Feynman)")
        print("  [3] learn       Study a specific chapter (1-21)")
        print("  [4] review      FSRS spaced-repetition due queue")
        print("  [5] interleave  Cross-chapter desirable-difficulty mixer")
        print("  [6] debug       Compiler & borrow-checker error clinic")
        print("  [7] feynman     Feynman self-explanation check")
        print("  [8] lab         Live rustc coding labs")
        print("  [9] ref         Appendices A-G quick reference")
        print("  [0] settings    Bionic Reading, retention target, sprint duration")
        print("  [q] quit        Exit RustForge")

        choice = engine.ui.prompt("Select mode").lower()
        if choice in ("q", "quit", "exit"):
            print(engine.ui.dim("\nProgress saved. See you next sprint."))
            return 0
        if choice in ("1", "map"):
            engine.run_map()
            engine.ui.pause()
        elif choice in ("2", "sprint"):
            engine.run_sprint()
        elif choice in ("3", "learn"):
            raw = engine.ui.prompt("Chapter number (1-21)")
            if raw.isdigit():
                engine.run_learn(int(raw))
        elif choice in ("4", "review"):
            engine.run_review()
        elif choice in ("5", "interleave"):
            engine.run_interleave()
        elif choice in ("6", "debug"):
            engine.run_debug()
        elif choice in ("7", "feynman"):
            raw = engine.ui.prompt("Chapter number (1-21, or Enter for random)")
            engine.run_feynman(int(raw) if raw.isdigit() else None)
        elif choice in ("8", "lab"):
            engine.run_lab()
        elif choice in ("9", "ref"):
            engine.run_reference()
        elif choice in ("0", "settings"):
            engine.run_settings()
        else:
            print(engine.ui.dim("  Unrecognized option. Pick 0-9 or 'q'."))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    store = ProgressStore.load(args.data_file)
    bionic = bool(args.bionic or store.settings.bionic_reading)
    ui = TerminalUI(use_color=not args.no_color, bionic=bionic)
    engine = LearningEngine(ui=ui, store=store)

    if args.command is None:
        return interactive_loop(engine)
    if args.command == "learn":
        engine.run_learn(args.chapter)
    elif args.command == "review":
        engine.run_review(limit=args.limit)
    elif args.command == "interleave":
        engine.run_interleave(count=args.count)
    elif args.command == "debug":
        engine.run_debug(chapter_num=args.chapter)
    elif args.command == "feynman":
        engine.run_feynman(chapter_num=args.chapter)
    elif args.command == "lab":
        engine.run_lab(chapter_num=args.chapter)
    elif args.command == "sprint":
        engine.run_sprint(minutes=args.minutes)
    elif args.command == "map":
        engine.run_map()
    elif args.command == "ref":
        engine.run_reference(code=args.appendix)
    elif args.command == "settings":
        engine.run_settings()
    return 0


if __name__ == "__main__":
    sys.exit(main())

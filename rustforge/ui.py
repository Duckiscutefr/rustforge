"""Monochrome high-contrast terminal UI with optional Bionic Reading for prose."""

from __future__ import annotations

import os
import re
import shutil
import sys
import textwrap
from typing import Iterable


class Ansi:
    """Monochrome ANSI escape codes (black/white/gray contrast, zero emojis)."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    INVERSE = "\033[7m"
    BRIGHT_WHITE = "\033[97m"
    GRAY = "\033[90m"


class TerminalUI:
    """Renders crisp, narrow-terminal-safe monochrome layouts with optional Bionic Reading."""

    def __init__(self, use_color: bool = True, bionic: bool = False, width: int | None = None) -> None:
        no_color = bool(os.environ.get("NO_COLOR"))
        is_tty = sys.stdout.isatty()
        self.use_color = use_color and not no_color and is_tty
        self.bionic = bionic
        self._fixed_width = width

    @property
    def width(self) -> int:
        if self._fixed_width is not None:
            return max(56, min(self._fixed_width, 100))
        cols = shutil.get_terminal_size((80, 24)).columns
        return max(56, min(cols - 2, 88))

    def style(self, text: str, *codes: str) -> str:
        if not self.use_color or not codes:
            return text
        return f"{''.join(codes)}{text}{Ansi.RESET}"

    def bold(self, text: str) -> str:
        return self.style(text, Ansi.BOLD, Ansi.BRIGHT_WHITE)

    def dim(self, text: str) -> str:
        return self.style(text, Ansi.DIM)

    def inverse(self, text: str) -> str:
        return self.style(text, Ansi.INVERSE, Ansi.BOLD)

    def underline(self, text: str) -> str:
        return self.style(text, Ansi.UNDERLINE)

    def bionic_word(self, word: str) -> str:
        """Bold fixation prefix of a single prose word without altering punctuation."""
        if not self.bionic or not self.use_color:
            return word
        match = re.match(r"^([^A-Za-z0-9]*)([A-Za-z]+)([^A-Za-z0-9]*)$", word)
        if not match:
            return word
        lead, core, trail = match.groups()
        n = len(core)
        if n <= 1:
            split = 1
        elif n <= 3:
            split = 1
        elif n <= 5:
            split = 2
        elif n <= 8:
            split = 3
        else:
            split = max(3, (n * 45) // 100)
        return f"{lead}{Ansi.BOLD}{core[:split]}{Ansi.RESET}{core[split:]}{trail}"

    def format_prose(self, text: str) -> str:
        """Apply Bionic Reading to prose while keeping inline `code` segments untouched."""
        if not self.bionic or not self.use_color:
            return text
        parts = re.split(r"(`[^`]+`)", text)
        rendered: list[str] = []
        for idx, part in enumerate(parts):
            if idx % 2 == 1:
                # Inline code: never apply bionic bolding
                rendered.append(self.style(part, Ansi.BRIGHT_WHITE))
            else:
                tokens = re.split(r"(\s+)", part)
                rendered.append("".join(self.bionic_word(tok) if tok and not tok.isspace() else tok for tok in tokens))
        return "".join(rendered)

    def hr(self, char: str = "-") -> str:
        return self.dim(char * self.width)

    def banner(self, title: str, subtitle: str = "") -> None:
        w = self.width
        print()
        print(self.bold("=" * w))
        print(self.inverse(f" {title.upper()} ".ljust(w)))
        if subtitle:
            print(self.dim(subtitle[:w]))
        print(self.bold("=" * w))

    def section(self, title: str) -> None:
        print()
        print(self.bold(f"[ {title.upper()} ]"))
        print(self.hr("-"))

    def paragraph(self, text: str, indent: int = 0) -> None:
        prefix = " " * indent
        wrap_width = max(40, self.width - indent)
        for raw_line in text.strip().splitlines():
            stripped = raw_line.strip()
            if not stripped:
                print()
                continue
            for line in textwrap.wrap(stripped, width=wrap_width):
                print(f"{prefix}{self.format_prose(line)}")

    def bullets(self, items: Iterable[str], indent: int = 2) -> None:
        prefix = " " * indent
        wrap_width = max(38, self.width - indent - 2)
        for item in items:
            wrapped = textwrap.wrap(item.strip(), width=wrap_width)
            if not wrapped:
                continue
            print(f"{prefix}* {self.format_prose(wrapped[0])}")
            for cont in wrapped[1:]:
                print(f"{prefix}  {self.format_prose(cont)}")

    def code_block(self, code: str, title: str = "RUST") -> None:
        """Render a code block verbatim (never applies Bionic Reading)."""
        w = self.width
        header = f"+-- {title} " + "-" * max(2, w - len(title) - 6) + "+"
        footer = "+" + "-" * max(2, w - 2) + "+"
        print(self.dim(header))
        for line in code.strip("\n").splitlines():
            print(f"{self.dim('|')} {line}")
        print(self.dim(footer))

    def diagram(self, ascii_art: str, title: str = "MEMORY MODEL") -> None:
        """Render an ASCII mental-model diagram verbatim (never applies Bionic Reading)."""
        w = self.width
        header = f"+== {title} " + "=" * max(2, w - len(title) - 6) + "+"
        footer = "+" + "=" * max(2, w - 2) + "+"
        print(self.bold(header))
        for line in ascii_art.strip("\n").splitlines():
            print(f"{self.dim('|')} {line}")
        print(self.bold(footer))

    def callout(self, label: str, body: str) -> None:
        print()
        print(self.inverse(f" {label.upper()} "))
        self.paragraph(body, indent=2)

    def progress_bar(self, ratio: float, width: int = 24) -> str:
        ratio = max(0.0, min(1.0, ratio))
        filled = int(round(ratio * width))
        return "[" + "#" * filled + "." * (width - filled) + f"] {int(ratio * 100):3d}%"

    def prompt(self, message: str, default: str = "") -> str:
        suffix = f" [{default}]" if default else ""
        try:
            raw = input(f"\n{self.bold('>')} {message}{suffix}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return "q"
        return raw if raw else default

    def pause(self, message: str = "Press Enter to continue (or 'q' to return)") -> bool:
        resp = self.prompt(message)
        return resp.lower() != "q"

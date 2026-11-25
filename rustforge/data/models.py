"""Typed curriculum data models for RustForge."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RecallCard:
    """Prediction-before-reveal active recall card scheduled by FSRS."""

    id: str
    chapter: int
    prompt: str
    code: str
    options: tuple[str, ...]
    answer_index: int  # 0-based index into options
    explanation: str
    tag: str = "recall"


@dataclass(frozen=True)
class ClozeDrill:
    """Generation-effect drill requiring exact Rust syntax production."""

    id: str
    chapter: int
    prompt: str
    code_template: str  # Contains ___ placeholder
    accepted_answers: tuple[str, ...]
    hint: str
    explanation: str


@dataclass(frozen=True)
class CompilerClinic:
    """Real rustc diagnostic debugging drill."""

    id: str
    chapter: int
    error_code: str
    title: str
    broken_code: str
    compiler_output: str
    question: str
    options: tuple[str, ...]
    answer_index: int
    fix_code: str
    mental_model: str


@dataclass(frozen=True)
class FeynmanPrompt:
    """Self-explanation prompt with rubric checklist and key-concept triggers."""

    chapter: int
    question: str
    rubric_points: tuple[str, ...]
    key_terms: tuple[str, ...]
    model_answer: str


@dataclass(frozen=True)
class CodingLab:
    """Live rustc --test coding challenge with starter code and reference solution."""

    id: str
    chapter: int
    title: str
    objective: str
    starter_code: str
    solution_code: str


@dataclass(frozen=True)
class Chapter:
    number: int
    title: str
    summary: str
    mental_model: str
    key_rules: tuple[str, ...]
    diagram_title: str
    diagram: str
    recall_cards: tuple[RecallCard, ...]
    cloze_drills: tuple[ClozeDrill, ...]
    clinic: CompilerClinic
    feynman: FeynmanPrompt
    lab: CodingLab | None = None


@dataclass(frozen=True)
class AppendixSection:
    code: str  # "A".."G"
    title: str
    summary: str
    entries: tuple[tuple[str, str], ...]
    notes: tuple[str, ...] = field(default_factory=tuple)

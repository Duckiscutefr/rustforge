"""Appendices A through G of The Rust Programming Language (2024 Edition)."""

from __future__ import annotations

from rustforge.data.models import AppendixSection

APPENDICES: list[AppendixSection] = [
    AppendixSection(
        code="A",
        title="Keywords & Raw Identifiers",
        summary="Strict keywords, reserved keywords (including `gen` in Rust 2024), weak keywords, and `r#` raw identifiers.",
        entries=(
            ("Strict (selected)", "as, async, await, break, const, continue, crate, dyn, else, enum, extern, false, fn, for, if, impl, in, let, loop, match, mod, move, mut, pub, ref, return, Self, self, static, struct, super, trait, true, type, unsafe, use, where, while"),
            ("Reserved (future)", "abstract, become, box, do, final, gen (2024), macro, override, priv, try, typeof, unsized, virtual, yield"),
            ("Weak keywords", "'static, macro_rules, raw, safe, union"),
            ("Raw identifiers", "Prefix with `r#` to use a keyword as an identifier (e.g., `fn r#match() {}` or `r#gen` in Edition 2024)."),
        ),
        notes=(
            "Rust 2024 reserved `gen` for future generator blocks; older crates using `gen` as a variable name can write `r#gen`.",
        ),
    ),
    AppendixSection(
        code="B",
        title="Operators and Symbols",
        summary="Key Rust operators, sigils, turbofish syntax, and lifetime/reference punctuation.",
        entries=(
            ("?", "Error / Option propagation operator (calls `From::from` on `Err`)"),
            ("::<>", "Turbofish: explicit generic type arguments in expressions (e.g., `s.parse::<u32>()`)"),
            ("& / &mut", "Immutable / mutable borrow or reference type"),
            ("&raw const / &raw mut", "Rust 2024 raw pointer creation without intermediate reference UB"),
            (".. / ..=", "Half-open range (`0..5` -> 0..4) vs. inclusive range (`0..=5` -> 0..5); also struct update & pattern rest"),
            ("=> / ->", "Match arm separator (`=>`) vs. function/closure return type (`->`)"),
            ("@", "Pattern binding while testing (`val @ 1..=10`)"),
            ("!", "Macro invocation (`vec!`), logical/bitwise NOT, or the never type (`fn exit() -> !`)"),
        ),
    ),
    AppendixSection(
        code="C",
        title="Derivable Traits",
        summary="Standard library traits generated automatically via `#[derive(...)]`.",
        entries=(
            ("Debug", "Programmer-facing formatting for `{:?}` and `{:#?}`"),
            ("PartialEq / Eq", "Equality (`==`, `!=`); `Eq` asserts reflexivity (not valid for `f32`/`f64` due to `NaN`)"),
            ("PartialOrd / Ord", "Ordering (`<`, `>`, `<=`, `>=`); `Ord` asserts total ordering (required for `BTreeMap` keys)"),
            ("Clone", "Explicit duplication via `.clone()` (may allocate on heap)"),
            ("Copy", "Implicit bitwise stack copy (requires `Clone`, incompatible with `Drop`)"),
            ("Hash", "Produces a hash value (required alongside `Eq` for `HashMap` / `HashSet` keys)"),
            ("Default", "Creates a sensible empty/zero value via `T::default()`"),
        ),
    ),
    AppendixSection(
        code="D",
        title="Useful Development Tools",
        summary="Official Rust ecosystem tools shipped with `rustup` and Cargo.",
        entries=(
            ("rustfmt (`cargo fmt`)", "Automatic formatting to official Rust style guidelines"),
            ("rustfix (`cargo fix`)", "Automatically applies compiler suggestions and edition migrations"),
            ("Clippy (`cargo clippy`)", "Hundreds of lints for idiomatic, faster, and bug-free Rust"),
            ("rust-analyzer", "IDE language server providing inlay types, go-to-definition, and quick fixes"),
            ("Miri (`cargo +nightly miri test`)", "Interpreter that detects undefined behavior in `unsafe` Rust"),
        ),
    ),
    AppendixSection(
        code="E",
        title="Editions (2015, 2018, 2021, 2024)",
        summary="How Rust evolves opt-in syntax every ~3 years without splitting the ecosystem.",
        entries=(
            ("Zero Ecosystem Split", "Crates on different editions (e.g., 2018 + 2024) compile and link seamlessly in one binary."),
            ("Migration", "Run `cargo fix --edition` to migrate automatically before bumping `edition = \"2024\"` in `Cargo.toml`."),
            ("2024 Highlights", "`gen` reserved, `unsafe extern`, `#[unsafe(no_mangle)]`, `&raw const`/`&raw mut`, Cargo `resolver = \"3\"`, RPIT lifetime capture rules, `if let` temporary scope tightening."),
        ),
    ),
    AppendixSection(
        code="F",
        title="Translations of the Book",
        summary="Community-maintained translations of The Rust Programming Language across dozens of languages.",
        entries=(
            ("Official Book", "https://doc.rust-lang.org/book/"),
            ("Translations Index", "Maintained by the Rust community via GitHub repositories linked from the official Book Appendix F."),
        ),
    ),
    AppendixSection(
        code="G",
        title="How Rust Is Made and 'Nightly Rust'",
        summary="The 6-week release train (Nightly -> Beta -> Stable), RFC process, and stability without stagnation.",
        entries=(
            ("Release Train", "Every 6 weeks: Nightly branches to Beta, and the previous Beta ships as Stable."),
            ("Feature Flags", "Unstable features live behind `#![feature(...)]` on Nightly only until stabilized via RFC."),
            ("Backwards Compatibility", "Stable Rust guarantees old code keeps compiling—stability without stagnation."),
        ),
    ),
]

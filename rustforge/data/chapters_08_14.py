"""Chapters 8 to 14 of The Rust Programming Language (2024 Edition)."""

from __future__ import annotations

from rustforge.data.models import (
    Chapter,
    ClozeDrill,
    CodingLab,
    CompilerClinic,
    FeynmanPrompt,
    RecallCard,
)

CHAPTERS_08_14: list[Chapter] = [
    Chapter(
        number=8,
        title="Common Collections: Vec, String & HashMap",
        summary="Heap-allocated collections, UTF-8 string internals, borrow-checker interactions, and Entry API.",
        mental_model=(
            "Unlike fixed-size arrays and tuples on the stack, `Vec<T>`, `String`, and `HashMap<K, V>` store "
            "their data on the heap and can grow dynamically. `String` is a UTF-8 wrapper over `Vec<u8>`—that is "
            "why `s[0]` is forbidden (a single byte may not be a valid Unicode scalar value!). `HashMap` uses "
            "SipHash by default for DoS resistance and offers the zero-double-lookup `entry().or_insert()` API."
        ),
        key_rules=(
            "`&v[i]` panics on out-of-bounds; `v.get(i)` returns `Option<&T>` safely.",
            "Holding an immutable reference to a `Vec` element prevents `v.push(...)` because pushing may reallocate the heap buffer.",
            "Iterate strings explicitly with `.chars()` (Unicode scalar values) or `.bytes()`, never raw integer indexing.",
            "`map.entry(k).or_insert(0)` returns `&mut V` so you can update in place with `*count += 1`.",
            "To store mixed types in one `Vec`, wrap them in an `enum`.",
        ),
        diagram_title="UTF-8 STRING LAYERS",
        diagram=(
            "  \"नमस्ते\" in memory:\n"
            "  Bytes (u8):    [224, 164, 168, 224, 164, 174, ...]  (18 bytes)\n"
            "  Scalars (char): ['न', 'म', 'स', '्', 'त', 'े']     (6 chars)\n"
            "  Graphemes:      [\"न\", \"म\", \"स्\", \"ते\"]            (4 clusters)\n"
            "  --> s[0] is ambiguous & O(1) impossible for chars -> FORBIDDEN"
        ),
        recall_cards=(
            RecallCard(
                id="ch08_c1",
                chapter=8,
                prompt="Why does `let first = &v[0]; v.push(6); println!(\"{first}\");` fail to compile?",
                code="let mut v = vec![1, 2, 3];\nlet first = &v[0];\nv.push(6);\nprintln!(\"{first}\");",
                options=(
                    "`Vec` elements cannot be borrowed",
                    "`v.push(6)` needs `&mut v` and could reallocate the heap buffer, leaving `first` dangling",
                    "`println!` consumes `first`",
                    "`vec!` creates an immutable vector even with `mut`",
                ),
                answer_index=1,
                explanation="If `v` is at capacity, `push` allocates a new buffer and frees the old one. `first` would become a dangling pointer, so the borrow checker forbids overlapping `&v[0]` and `&mut v`.",
            ),
            RecallCard(
                id="ch08_c2",
                chapter=8,
                prompt="What happens to `s1` and `s2` in `let s3 = s1 + &s2;`?",
                code='let s1 = String::from("Hello, ");\nlet s2 = String::from("world!");\nlet s3 = s1 + &s2;',
                options=(
                    "Both s1 and s2 remain valid",
                    "`s1` is MOVED into `s3` (no longer valid), while `s2` is only borrowed and remains valid",
                    "Both s1 and s2 are moved",
                    "`s2` is moved and `s1` remains valid",
                ),
                answer_index=1,
                explanation="`String::add` has signature `fn add(self, s: &str) -> String`. It takes ownership of `s1`, appends `&s2` (deref-coerced from `&String` to `&str`), and returns the buffer.",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch08_cl1",
                chapter=8,
                prompt="Count word frequencies using the HashMap Entry API:",
                code_template="let count = map.___(word).or_insert(0);\n*count += 1;",
                accepted_answers=("entry",),
                hint="Method that returns an Entry enum (Occupied or Vacant).",
                explanation="`map.entry(word).or_insert(0)` inserts 0 if missing and returns `&mut i32` to the value.",
            ),
        ),
        clinic=CompilerClinic(
            id="ch08_err",
            chapter=8,
            error_code="E0277",
            title="Indexing a `String` by integer",
            broken_code='let s = String::from("hello");\nlet ch = s[0];',
            compiler_output=(
                "error[E0277]: the type `str` cannot be indexed by `{integer}`\n"
                " --> src/main.rs:2:12\n"
                "  |\n"
                "2 | let ch = s[0];\n"
                "  |            ^ string indices are ranges of `usize`\n"
                "  = note: you can use `.chars().nth()` or `.bytes().nth()`"
            ),
            question="Why does Rust forbid `s[0]` on `String`?",
            options=(
                "UTF-8 characters take 1–4 bytes, so O(1) character indexing is impossible and byte indexing could split a character",
                "Strings are stored as linked lists",
                "Only `Vec<char>` exists in std",
                "Indexing requires `unsafe` in all collections",
            ),
            answer_index=0,
            fix_code='let s = String::from("hello");\nlet ch = s.chars().next();',
            mental_model="UTF-8 is variable-width. Explicitly choose `.bytes()` or `.chars()` so you never silently corrupt Unicode.",
        ),
        feynman=FeynmanPrompt(
            chapter=8,
            question="Explain why borrowing element 0 of a `Vec` blocks calling `v.push(...)` even though `push` adds to the END of the vector.",
            rubric_points=(
                "A Vec stores elements contiguously in a single heap allocation.",
                "When length exceeds capacity, push allocates a larger buffer, copies elements, and frees the old buffer.",
                "Any existing reference to element 0 would point to freed memory (dangling pointer).",
            ),
            key_terms=("contiguous", "reallocate", "capacity", "dangling", "borrow"),
            model_answer=(
                "A `Vec` keeps all elements next to each other in one heap block. If pushing a new item exceeds "
                "its capacity, the `Vec` allocates a bigger block, moves all items, and frees the old memory—which "
                "would leave a reference to `v[0]` pointing at freed memory."
            ),
        ),
        lab=CodingLab(
            id="lab_ch08_freq",
            chapter=8,
            title="Word Frequency Counter with Entry API",
            objective="Implement `word_counts(text: &str) -> HashMap<String, usize>` (lowercased, whitespace-split) using `entry().or_insert(0)`.",
            starter_code=(
                "use std::collections::HashMap;\n\n"
                "pub fn word_counts(text: &str) -> HashMap<String, usize> {\n"
                "    todo!()\n"
                "}\n\n"
                "#[cfg(test)]\n"
                "mod tests {\n"
                "    use super::*;\n"
                "    #[test]\n"
                "    fn counts_words() {\n"
                '        let m = word_counts("Rust rust SAFE safe rust");\n'
                '        assert_eq!(m.get("rust"), Some(&3));\n'
                '        assert_eq!(m.get("safe"), Some(&2));\n'
                '        assert_eq!(m.get("python"), None);\n'
                "    }\n"
                "}\n"
            ),
            solution_code=(
                "use std::collections::HashMap;\n\n"
                "pub fn word_counts(text: &str) -> HashMap<String, usize> {\n"
                "    let mut map = HashMap::new();\n"
                "    for word in text.split_whitespace() {\n"
                "        *map.entry(word.to_lowercase()).or_insert(0) += 1;\n"
                "    }\n"
                "    map\n"
                "}\n"
            ),
        ),
    ),
    Chapter(
        number=9,
        title="Error Handling: panic!, Result & ?",
        summary="Unrecoverable panics vs. recoverable Result, error propagation with `?`, and validation newtypes.",
        mental_model=(
            "Rust has no exceptions. Errors split cleanly into two worlds: unrecoverable bugs/invariant violations "
            "(`panic!`) and recoverable failures (`Result<T, E>`). The `?` operator propagates `Err(e)` upward "
            "automatically while converting `e` via the `From` trait into the function's return error type."
        ),
        key_rules=(
            "Use `panic = 'abort'` in `[profile.release]` to shrink binary size by omitting stack unwinding tables.",
            "Set `RUST_BACKTRACE=1` to inspect full stack frames when a panic occurs.",
            "`?` works in functions returning `Result` or `Option` (never mix `Result` and `Option` without `.ok()` or `.ok_or(...)`).",
            "`fn main() -> Result<(), Box<dyn std::error::Error>>` lets you use `?` directly inside `main`.",
            "Encode domain invariants in types (e.g., `struct Guess(i32)` with private field + validating constructor) so invalid states cannot exist.",
        ),
        diagram_title="THE `?` OPERATOR DESUGARED",
        diagram=(
            "  let text = fs::read_to_string(path)?;\n"
            "  ================ expands to ================\n"
            "  let text = match fs::read_to_string(path) {\n"
            "      Ok(val) => val,\n"
            "      Err(e)  => return Err(From::from(e)),\n"
            "  };"
        ),
        recall_cards=(
            RecallCard(
                id="ch09_c1",
                chapter=9,
                prompt="When you use `?` on a `Result<T, io::Error>` inside a function returning `Result<T, MyError>`, what trait must be implemented?",
                code="fn load() -> Result<String, MyError> {\n    let s = std::fs::read_to_string(\"a.txt\")?;\n    Ok(s)\n}",
                options=(
                    "`Copy` on `MyError`",
                    "`From<io::Error>` for `MyError`",
                    "`Default` for `MyError`",
                    "`Drop` for `io::Error`",
                ),
                answer_index=1,
                explanation="The `?` operator calls `From::from` on the error value to convert `io::Error` into `MyError` seamlessly.",
            ),
            RecallCard(
                id="ch09_c2",
                chapter=9,
                prompt="Can you use `?` on an `Option<T>` inside a function returning `Result<T, E>` directly?",
                code="fn first_char(s: &str) -> Result<char, String> {\n    Ok(s.chars().next()?)\n}",
                options=(
                    "Yes, None automatically becomes Err(\"\")",
                    "No: `?` does not automatically convert between `Option` and `Result`; use `.ok_or(...)` first",
                    "Yes, in Edition 2024",
                    "Only if E implements Default",
                ),
                answer_index=1,
                explanation="`?` requires matching residual types. Convert `Option` to `Result` via `.ok_or(err)` or `.ok_or_else(|| ...)` before applying `?`.",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch09_cl1",
                chapter=9,
                prompt="Propagate any error from `read_to_string` cleanly:",
                code_template="fn read_name() -> Result<String, std::io::Error> {\n    let s = std::fs::read_to_string(\"name.txt\")___;\n    Ok(s)\n}",
                accepted_answers=("?",),
                hint="Single-character error propagation operator.",
                explanation="`?` returns `Err(e)` early on failure or unwraps `Ok(val)` on success.",
            ),
        ),
        clinic=CompilerClinic(
            id="ch09_err",
            chapter=9,
            error_code="E0277",
            title="Using `?` in `fn main()` returning `()`",
            broken_code='use std::fs::File;\nfn main() {\n    let _f = File::open("hello.txt")?;\n}',
            compiler_output=(
                "error[E0277]: the `?` operator can only be used in a function that returns `Result` or `Option`\n"
                " --> src/main.rs:3:37\n"
                "  |\n"
                '3 |     let _f = File::open("hello.txt")?;\n'
                "  |                                     ^ cannot use the `?` operator in a function that returns `()`"
            ),
            question="How do you enable `?` inside `main`?",
            options=(
                "Change `fn main()` to `fn main() -> Result<(), Box<dyn std::error::Error>>` and end with `Ok(())`",
                "Add `#[allow(errors)]` above `main`",
                "Replace `?` with `!`",
                "Import `std::error::Question`",
            ),
            answer_index=0,
            fix_code='use std::error::Error;\nuse std::fs::File;\nfn main() -> Result<(), Box<dyn Error>> {\n    let _f = File::open("hello.txt")?;\n    Ok(())\n}',
            mental_model="`?` performs an early `return Err(...)`, so the enclosing function's return type must be compatible (`Result` or `Option`).",
        ),
        feynman=FeynmanPrompt(
            chapter=9,
            question="When should Rust code `panic!` versus returning a `Result<T, E>`?",
            rubric_points=(
                "Return Result when failure is expected/recoverable (missing file, bad user input, network error).",
                "Panic when a program invariant/contract is violated, in tests/prototypes, or when continuing would be unsafe/corrupt.",
                "Using custom validating types (like `Guess`) avoids repeated runtime checks.",
            ),
            key_terms=("Result", "panic", "recoverable", "contract", "invariant"),
            model_answer=(
                "Return `Result` whenever a caller could reasonably expect and recover from failure (I/O, parsing, "
                "network). Use `panic!` when a bug breaks a core invariant or contract where no safe recovery exists, "
                "or in quick prototypes and tests."
            ),
        ),
        lab=CodingLab(
            id="lab_ch09_parse",
            chapter=9,
            title="Validating Port Newtype & `?` Propagation",
            objective="Implement `Port::parse(s: &str) -> Result<Port, String>` rejecting non-numbers and port 0.",
            starter_code=(
                "#[derive(Debug, PartialEq)]\n"
                "pub struct Port(u16);\n\n"
                "impl Port {\n"
                "    pub fn parse(s: &str) -> Result<Self, String> {\n"
                "        // TODO: parse u16 (mapping parse error to String) and reject 0\n"
                "        todo!()\n"
                "    }\n"
                "    pub fn value(&self) -> u16 { self.0 }\n"
                "}\n\n"
                "#[cfg(test)]\n"
                "mod tests {\n"
                "    use super::*;\n"
                "    #[test]\n"
                "    fn validates_ports() {\n"
                '        assert_eq!(Port::parse("8080").unwrap().value(), 8080);\n'
                '        assert!(Port::parse("0").is_err());\n'
                '        assert!(Port::parse("99999").is_err());\n'
                '        assert!(Port::parse("abc").is_err());\n'
                "    }\n"
                "}\n"
            ),
            solution_code=(
                "impl Port {\n"
                "    pub fn parse(s: &str) -> Result<Self, String> {\n"
                "        let num: u16 = s.trim().parse().map_err(|e| format!(\"invalid port: {e}\"))?;\n"
                "        if num == 0 {\n"
                "            return Err(\"port cannot be 0\".to_string());\n"
                "        }\n"
                "        Ok(Self(num))\n"
                "    }\n"
                "    pub fn value(&self) -> u16 { self.0 }\n"
                "}\n"
            ),
        ),
    ),
    Chapter(
        number=10,
        title="Generic Types, Traits, and Lifetimes",
        summary="Monomorphization, trait bounds & coherence (orphan rule), lifetime annotations `'a`, and the 3 elision rules.",
        mental_model=(
            "Generics have ZERO runtime cost because `rustc` performs monomorphization (generating specialized "
            "machine code for each concrete type used). Traits define shared behavior like interfaces, guarded by "
            "the orphan rule. Lifetimes (`'a`) do NOT change how long values live—they describe relationships "
            "between input and output reference lifetimes so the borrow checker can prove outputs never dangle."
        ),
        key_rules=(
            "Orphan rule (coherence): you can implement a trait on a type ONLY if either the trait OR the type is local to your crate.",
            "3 Lifetime Elision Rules: (1) each input ref gets its own lifetime; (2) if there is 1 input lifetime, it applies to all outputs; (3) if `&self`/`&mut self` is present, its lifetime applies to all outputs.",
            "`'static` means a reference CAN live for the entire program (e.g., string literals), NOT that it must live forever.",
            "Blanket implementations (`impl<T: Display> ToString for T`) implement a trait for every type satisfying a bound.",
        ),
        diagram_title="LIFETIME RELATIONSHIP `'a`",
        diagram=(
            "  fn longest<'a>(x: &'a str, y: &'a str) -> &'a str\n"
            "  \n"
            "  x lives: |=============================|\n"
            "  y lives:     |================|\n"
            "  'a is:       |================|  (the SHORTER overlap!)\n"
            "  Return ref cannot outlive 'a (the shorter of x and y)."
        ),
        recall_cards=(
            RecallCard(
                id="ch10_c1",
                chapter=10,
                prompt="Do lifetime annotations like `'a` extend how long a referenced value stays alive in memory?",
                code="fn longest<'a>(x: &'a str, y: &'a str) -> &'a str",
                options=(
                    "Yes, `'a` keeps both values alive on the heap",
                    "No: `'a` only describes the relationship between lifetimes so the borrow checker can reject dangling references",
                    "Yes, `'a` promotes stack references to `'static`",
                    "Only when combined with `mut`",
                ),
                answer_index=1,
                explanation="Lifetimes are purely compile-time constraints. `'a` tells the compiler the returned reference lives at most as long as the shorter of `x` and `y`.",
            ),
            RecallCard(
                id="ch10_c2",
                chapter=10,
                prompt="Why does `impl std::fmt::Display for Vec<i32>` fail to compile in your own crate?",
                code="impl std::fmt::Display for Vec<i32> { ... }",
                options=(
                    "`Vec` already implements `Display`",
                    "Orphan rule: neither `Display` nor `Vec` is defined in your crate",
                    "Generics cannot implement `Display`",
                    "`Display` is a marker trait",
                ),
                answer_index=1,
                explanation="The orphan rule prevents two external crates from writing conflicting trait implementations for the same type. Wrap `Vec` in a local newtype struct instead.",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch10_cl1",
                chapter=10,
                prompt="Annotate `longest` so the return slice ties to both input slices:",
                code_template="fn longest<___>(x: &'a str, y: &'a str) -> &'a str {\n    if x.len() > y.len() { x } else { y }\n}",
                accepted_answers=("'a",),
                hint="Generic lifetime parameter name.",
                explanation="Lifetime parameters start with an apostrophe (`'a`) and are declared in `<>`.",
            ),
        ),
        clinic=CompilerClinic(
            id="ch10_err",
            chapter=10,
            error_code="E0106",
            title="Missing lifetime specifier on returned reference",
            broken_code="fn longest(x: &str, y: &str) -> &str {\n    if x.len() > y.len() { x } else { y }\n}",
            compiler_output=(
                "error[E0106]: missing lifetime specifier\n"
                " --> src/main.rs:1:33\n"
                "  |\n"
                "1 | fn longest(x: &str, y: &str) -> &str {\n"
                "  |               ----     ----     ^ expected named lifetime parameter\n"
                "  = help: this function's return type contains a borrowed value, but the signature does not say whether it is borrowed from `x` or `y`"
            ),
            question="Why couldn't Rust's 3 lifetime elision rules infer the return lifetime here?",
            options=(
                "There are TWO input references and no `&self`, so rules 2 and 3 do not apply",
                "String slices never support lifetime elision",
                "Functions with `if` cannot use elision",
                "Elision only works in `unsafe` blocks",
            ),
            answer_index=0,
            fix_code="fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {\n    if x.len() > y.len() { x } else { y }\n}",
            mental_model="Elision handles the common single-input and `&self` cases automatically. When multiple inputs could be returned, connect them explicitly with `'a`.",
        ),
        feynman=FeynmanPrompt(
            chapter=10,
            question="Explain monomorphization and why Rust generics have zero runtime performance penalty.",
            rubric_points=(
                "At compile time, rustc inspects every concrete type used with a generic function/struct.",
                "It generates specialized concrete copies of the code for each type (e.g., Option_i32, Option_f64).",
                "At runtime, there is no boxing, vtable lookup, or type-erasure overhead.",
            ),
            key_terms=("compile time", "concrete", "specialized", "vtable", "zero"),
            model_answer=(
                "During compilation, `rustc` replaces generic parameters with the exact concrete types your code "
                "uses, generating specialized machine code for each one. Because dispatch is resolved at compile "
                "time, generics run just as fast as hand-written concrete functions."
            ),
        ),
        lab=CodingLab(
            id="lab_ch10_largest",
            chapter=10,
            title="Generic Slice Maximum with Lifetimes & Traits",
            objective="Implement `largest_ref<T: PartialOrd>(list: &[T]) -> Option<&T>` without cloning elements.",
            starter_code=(
                "pub fn largest_ref<T: PartialOrd>(list: &[T]) -> Option<&T> {\n"
                "    todo!()\n"
                "}\n\n"
                "#[cfg(test)]\n"
                "mod tests {\n"
                "    use super::*;\n"
                "    #[test]\n"
                "    fn finds_largest() {\n"
                "        assert_eq!(largest_ref(&[3, 9, 2, 7]), Some(&9));\n"
                '        assert_eq!(largest_ref(&["apple", "zebra", "mango"]), Some(&"zebra"));\n'
                "        assert_eq!(largest_ref::<i32>(&[]), None);\n"
                "    }\n"
                "}\n"
            ),
            solution_code=(
                "pub fn largest_ref<T: PartialOrd>(list: &[T]) -> Option<&T> {\n"
                "    let mut largest = list.first()?;\n"
                "    for item in &list[1..] {\n"
                "        if item > largest {\n"
                "            largest = item;\n"
                "        }\n"
                "    }\n"
                "    Some(largest)\n"
                "}\n"
            ),
        ),
    ),
    Chapter(
        number=11,
        title="Writing Automated Tests",
        summary="Unit tests (`#[cfg(test)]`), integration tests (`tests/`), `should_panic`, `Result` tests, and `cargo test` flags.",
        mental_model=(
            "Testing is built straight into Cargo. Unit tests live alongside private code inside `#[cfg(test)] mod tests` "
            "(compiled ONLY during `cargo test`), while integration tests live in `tests/*.rs` and exercise only your "
            "library's public API as an external consumer would."
        ),
        key_rules=(
            "Tests run in parallel by default and capture stdout; pass `-- --test-threads=1` for serial execution or `-- --show-output` to see `println!`.",
            "`assert_eq!` and `assert_ne!` require `PartialEq` and `Debug` on the compared types.",
            "Use `#[should_panic(expected = \"substring\")]` to ensure a test panics for the RIGHT reason.",
            "Binary-only crates (`src/main.rs` without `src/lib.rs`) cannot have external integration tests in `tests/`.",
            "Mark slow tests with `#[ignore]` and run them on demand via `cargo test -- --ignored`.",
        ),
        diagram_title="UNIT VS. INTEGRATION TEST SCOPE",
        diagram=(
            "  src/lib.rs\n"
            "   +-- fn private_helper()     <-- tested by #[cfg(test)] mod tests\n"
            "   +-- pub fn public_api()     <-- tested by tests/integration.rs\n"
            "  tests/common/mod.rs          <-- shared helper (NOT run as test file)"
        ),
        recall_cards=(
            RecallCard(
                id="ch11_c1",
                chapter=11,
                prompt="What does `#[cfg(test)]` on `mod tests` tell Cargo?",
                code="#[cfg(test)]\nmod tests { ... }",
                options=(
                    "Run tests sequentially",
                    "Compile and include `mod tests` ONLY when running `cargo test`, not in `cargo build`",
                    "Export test functions to downstream crates",
                    "Enable debug assertions in release builds",
                ),
                answer_index=1,
                explanation="`#[cfg(test)]` strips test code from normal builds, saving compile time and keeping production binaries lean.",
            ),
            RecallCard(
                id="ch11_c2",
                chapter=11,
                prompt="Why should shared helper code for integration tests live in `tests/common/mod.rs` instead of `tests/common.rs`?",
                code="tests/\n  common/mod.rs\n  api_test.rs",
                options=(
                    "Cargo treats every top-level `tests/*.rs` file as a separate test crate, whereas subdirectories like `common/mod.rs` are not run as standalone tests",
                    "`tests/common.rs` is a syntax error",
                    "Rust 2024 forbids `.rs` files in `tests/`",
                    "Only `mod.rs` can contain `pub fn`",
                ),
                answer_index=0,
                explanation="Placing helpers in `tests/common/mod.rs` prevents Cargo from reporting an empty `common` test binary in test output.",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch11_cl1",
                chapter=11,
                prompt="Assert that a test panics with a message containing 'out of range':",
                code_template='#[test]\n#[___(expected = "out of range")]\nfn rejects_zero() { Guess::new(0); }',
                accepted_answers=("should_panic",),
                hint="Attribute that expects a panic.",
                explanation="`#[should_panic(expected = \"...\")]` verifies both that a panic occurred and that its message matches.",
            ),
        ),
        clinic=CompilerClinic(
            id="ch11_err",
            chapter=11,
            error_code="E0369",
            title="`assert_eq!` on custom struct missing `PartialEq`",
            broken_code=(
                "#[derive(Debug)]\n"
                "struct Score(u32);\n"
                "#[test]\n"
                "fn check() { assert_eq!(Score(10), Score(10)); }"
            ),
            compiler_output=(
                "error[E0369]: binary operation `==` cannot be applied to type `Score`\n"
                " --> src/lib.rs:4:14\n"
                "  |\n"
                "4 | fn check() { assert_eq!(Score(10), Score(10)); }\n"
                "  |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
            ),
            question="Which two traits must a type implement for `assert_eq!`?",
            options=(
                "`PartialEq` and `Debug`",
                "`Copy` and `Display`",
                "`Ord` and `Clone`",
                "`Eq` and `Hash`",
            ),
            answer_index=0,
            fix_code="#[derive(Debug, PartialEq)]\nstruct Score(u32);",
            mental_model="`assert_eq!` uses `==` (`PartialEq`) to compare values and `{:?}` (`Debug`) to print both sides if the assertion fails.",
        ),
        feynman=FeynmanPrompt(
            chapter=11,
            question="Explain the difference between unit tests and integration tests in Cargo, and why binary crates often split logic into `src/lib.rs`.",
            rubric_points=(
                "Unit tests live in `#[cfg(test)] mod tests` inside source files and can test private functions.",
                "Integration tests live in `tests/` and only call the public API of `src/lib.rs`.",
                "Keeping `src/main.rs` thin and putting logic in `src/lib.rs` makes the code testable by integration tests.",
            ),
            key_terms=("unit", "integration", "private", "public", "lib.rs"),
            model_answer=(
                "Unit tests sit inside each file's `#[cfg(test)]` module and can inspect private helpers. "
                "Integration tests in `tests/` compile as external crates and test only the public API of `src/lib.rs`, "
                "which is why keeping `src/main.rs` minimal and moving core logic to `src/lib.rs` is standard practice."
            ),
        ),
    ),
    Chapter(
        number=12,
        title="An I/O Project: Building `minigrep`",
        summary="Separation of concerns (`main.rs` vs `lib.rs`), CLI arg parsing, `Config::build`, env vars, and stderr vs stdout.",
        mental_model=(
            "Real Rust CLI tools keep `main.rs` tiny: parse arguments, call `lib::run(config)`, and print errors "
            "to `stderr` via `eprintln!` with a non-zero exit code (`process::exit(1)`). Moving `Config` and "
            "`search` into `lib.rs` makes every piece cleanly unit-testable with TDD."
        ),
        key_rules=(
            "`env::args()` panics on invalid Unicode; use `env::args_os()` if arbitrary OS strings must be handled.",
            "Print errors with `eprintln!` (stderr) so users redirecting `stdout > out.txt` still see errors on screen.",
            "Returning `Result<(), Box<dyn Error>>` from `run` lets callers decide how to format errors or exit.",
            "Keep `Config::build` separate from `run` so argument validation and file execution are independently testable.",
        ),
        diagram_title="MINIGREP ARCHITECTURE",
        diagram=(
            "  main.rs (thin shell)            lib.rs (testable core)\n"
            "  +--------------------+          +-------------------------+\n"
            "  | env::args()        | -------> | Config::build(args)     |\n"
            "  | eprintln! on Err   | <------- | run(config) -> Result   |\n"
            "  | process::exit(1)   |          | search(query, contents) |\n"
            "  +--------------------+          +-------------------------+"
        ),
        recall_cards=(
            RecallCard(
                id="ch12_c1",
                chapter=12,
                prompt="Why does `minigrep` write error messages with `eprintln!` instead of `println!`?",
                code='eprintln!("Application error: {e}");\nprocess::exit(1);',
                options=(
                    "`eprintln!` is faster than `println!`",
                    "`eprintln!` writes to standard error (`stderr`), keeping redirected `stdout` output files clean",
                    "`println!` cannot format `Box<dyn Error>`",
                    "`eprintln!` automatically calls `process::exit(1)`",
                ),
                answer_index=1,
                explanation="Separating data (`stdout`) from diagnostics (`stderr`) lets users pipe `minigrep foo file.txt > results.txt` without polluting `results.txt` with error messages.",
            ),
            RecallCard(
                id="ch12_c2",
                chapter=12,
                prompt="In `pub fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str>`, why is `'a` attached to `contents` and NOT `query`?",
                code="pub fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str>",
                options=(
                    "Because `query` is always `'static`",
                    "Because the returned line slices borrow directly from `contents`, not from `query`",
                    "Because Rust only allows one lifetime per function",
                    "Because `Vec` requires `'a` on its second argument",
                ),
                answer_index=1,
                explanation="The output slices point into `contents`. Attaching `'a` only to `contents` lets `query` be dropped earlier without invalidating the search results.",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch12_cl1",
                chapter=12,
                prompt="Check if the `IGNORE_CASE` environment variable is set (regardless of value):",
                code_template='let ignore_case = std::env::___("IGNORE_CASE").is_ok();',
                accepted_answers=("var",),
                hint="Function in `std::env` that reads an environment variable into `Result<String, VarError>`.",
                explanation="`std::env::var(\"IGNORE_CASE\").is_ok()` returns `true` whenever the env var is present.",
            ),
        ),
        clinic=CompilerClinic(
            id="ch12_err",
            chapter=12,
            error_code="E0597",
            title="Returned slice outlives `contents`",
            broken_code=(
                "fn bad_search(query: &str) -> Vec<&str> {\n"
                "    let contents = String::from(\"rust\\nfast\");\n"
                "    contents.lines().filter(|l| l.contains(query)).collect()\n"
                "}"
            ),
            compiler_output=(
                "error[E0597]: `contents` does not live long enough\n"
                " --> src/lib.rs:3:5\n"
                "  |\n"
                "3 |     contents.lines().filter(|l| l.contains(query)).collect()\n"
                "  |     ^^^^^^^^ borrowed value does not live long enough"
            ),
            question="How do you fix `bad_search`?",
            options=(
                "Either take `contents: &'a str` from the caller OR return `Vec<String>` (owned lines)",
                "Add `'static` to `query`",
                "Use `clone()` on `contents`",
                "Mark `contents` as `mut`",
            ),
            answer_index=0,
            fix_code="fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {\n    contents.lines().filter(|l| l.contains(query)).collect()\n}",
            mental_model="You can never return references into a local `String` created inside the same function; either borrow from the caller or return owned `String`s.",
        ),
        feynman=FeynmanPrompt(
            chapter=12,
            question="Explain why `search<'a>(query: &str, contents: &'a str) -> Vec<&'a str>` connects `'a` to `contents` instead of `query`.",
            rubric_points=(
                "Each element in the returned Vec is a slice pointing into `contents`.",
                "The returned slices do not point into `query`.",
                "Tying `'a` only to `contents` tells the borrow checker the results live as long as `contents`, even if `query` is dropped sooner.",
            ),
            key_terms=("slice", "contents", "query", "lifetime", "borrow"),
            model_answer=(
                "The returned `Vec<&'a str>` holds slices pointing directly into the text of `contents`, not `query`. "
                "Linking `'a` only to `contents` lets the caller drop `query` freely while keeping the matched lines valid."
            ),
        ),
    ),
    Chapter(
        number=13,
        title="Functional Features: Closures & Iterators",
        summary="Capture modes (`Fn`, `FnMut`, `FnOnce`), `move` closures, lazy iterators, adapters, and zero-cost abstractions.",
        mental_model=(
            "Closures capture their environment in the least restrictive way possible: immutable borrow (`&T`), "
            "mutable borrow (`&mut T`), or move (`T`). Iterators are LAZY state machines—chaining `.map().filter()` "
            "does zero work until a consuming adapter (`.collect()`, `.sum()`, `.for_each()`) drives `.next()`. "
            "LLVM unrolls iterator pipelines into loops as fast as—or faster than—manual indexing."
        ),
        key_rules=(
            "Every closure implements `FnOnce` (callable at least once); closures that don't move captured values out also implement `FnMut`; closures that don't mutate captured values also implement `Fn`.",
            "`move |x| ...` forces the closure to take ownership of captured variables (essential when sending closures to threads).",
            "Iterator adapters (`.map`, `.filter`, `.enumerate`) are lazy and produce a warning if unused.",
            "`.iter()` yields `&T`, `.iter_mut()` yields `&mut T`, and `.into_iter()` consumes the collection and yields owned `T`.",
        ),
        diagram_title="CLOSURE TRAIT HIERARCHY",
        diagram=(
            "  FnOnce  (may consume captured values; callable >= 1 time)\n"
            "    ^\n"
            "    |  subtrait\n"
            "  FnMut   (may mutate captured values; callable many times)\n"
            "    ^\n"
            "    |  subtrait\n"
            "  Fn      (reads captured values or captures nothing)"
        ),
        recall_cards=(
            RecallCard(
                id="ch13_c1",
                chapter=13,
                prompt="What does `let v = vec![1, 2, 3]; v.iter().map(|x| x + 1);` actually compute?",
                code="let v = vec![1, 2, 3];\nv.iter().map(|x| x + 1);",
                options=(
                    "It mutates `v` in place to `[2, 3, 4]`",
                    "Nothing! `map` is lazy and never executes without a consuming adapter like `.collect()`",
                    "It allocates a new `Vec` and drops it",
                    "It panics at runtime",
                ),
                answer_index=1,
                explanation="Iterators are lazy in Rust. `rustc` even warns: `unused Map that must be used`.",
            ),
            RecallCard(
                id="ch13_c2",
                chapter=13,
                prompt="Which closure trait does `Option::unwrap_or_else<F>` require, and why?",
                code="pub fn unwrap_or_else<F>(self, f: F) -> T where F: FnOnce() -> T",
                options=(
                    "`Fn` so it can be called in parallel",
                    "`FnOnce` because `f` is called AT MOST ONCE (only on `None`), allowing the widest range of closures",
                    "`FnMut` because it mutates `self`",
                    "`Copy` because `Option` is small",
                ),
                answer_index=1,
                explanation="Accepting `FnOnce` is the MOST permissive bound for callers: any `Fn`, `FnMut`, or `FnOnce` closure satisfies it.",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch13_cl1",
                chapter=13,
                prompt="Consume an iterator of `i32` values into a `Vec<i32>`:",
                code_template="let doubled: Vec<i32> = v.iter().map(|x| x * 2).___();",
                accepted_answers=("collect",),
                hint="Consuming adapter that gathers iterator items into a collection.",
                explanation="`.collect()` drives the iterator to completion and builds the target collection.",
            ),
        ),
        clinic=CompilerClinic(
            id="ch13_err",
            chapter=13,
            error_code="E0502",
            title="Printing a `Vec` while a `FnMut` closure borrows it mutably",
            broken_code=(
                "let mut list = vec![1, 2, 3];\n"
                "let mut borrows_mut = || list.push(7);\n"
                'println!("{list:?}");\n'
                "borrows_mut();"
            ),
            compiler_output=(
                "error[E0502]: cannot borrow `list` as immutable because it is also borrowed as mutable\n"
                " --> src/main.rs:3:11\n"
                "  |\n"
                "2 | let mut borrows_mut = || list.push(7);\n"
                "  |                       -- ---- first borrow occurs due to use of `list` in closure\n"
                '3 | println!("{list:?}");\n'
                "  |           ^^^^ immutable borrow occurs here\n"
                "4 | borrows_mut();\n"
                "  | ----------- mutable borrow later used here"
            ),
            question="Why does line 3 fail even though `borrows_mut()` hasn't been called yet?",
            options=(
                "Defining the closure immediately captures `&mut list`, and that mutable borrow lasts until `borrows_mut()` is last called on line 4",
                "Closures cannot capture `Vec`",
                "`println!` requires `&mut list`",
                "`borrows_mut` needs `move`",
            ),
            answer_index=0,
            fix_code='let mut list = vec![1, 2, 3];\nlet mut borrows_mut = || list.push(7);\nborrows_mut();\nprintln!("{list:?}");',
            mental_model="A closure's captured borrows stay active from definition until the closure's last use. Call `borrows_mut()` first, then print `list`.",
        ),
        feynman=FeynmanPrompt(
            chapter=13,
            question="Explain why Rust's iterator chains (`iter().filter().map().sum()`) are called 'zero-cost abstractions'.",
            rubric_points=(
                "Iterators are lazy and do not allocate intermediate collections between steps.",
                "Monomorphization and LLVM inlining compile the chain down to the same tight machine loop as hand-written code.",
                "They even eliminate bounds checks that manual `v[i]` indexing often incurs.",
            ),
            key_terms=("lazy", "allocate", "inline", "zero-cost", "loop"),
            model_answer=(
                "Iterator chains don't build intermediate vectors at each step; they compose lightweight structs that "
                "LLVM inlines and unrolls into a single tight machine loop—giving you high-level readability with "
                "no runtime overhead over a manual loop."
            ),
        ),
        lab=CodingLab(
            id="lab_ch13_iter",
            chapter=13,
            title="Zero-Allocation Iterator Pipeline",
            objective="Implement `sum_even_squares(nums: &[i32]) -> i32` using iterator adapters (`iter`, `filter`, `map`, `sum`).",
            starter_code=(
                "pub fn sum_even_squares(nums: &[i32]) -> i32 {\n"
                "    todo!()\n"
                "}\n\n"
                "#[cfg(test)]\n"
                "mod tests {\n"
                "    use super::*;\n"
                "    #[test]\n"
                "    fn computes_pipeline() {\n"
                "        assert_eq!(sum_even_squares(&[1, 2, 3, 4, 5]), 20);\n"
                "        assert_eq!(sum_even_squares(&[1, 3, 5]), 0);\n"
                "        assert_eq!(sum_even_squares(&[]), 0);\n"
                "    }\n"
                "}\n"
            ),
            solution_code=(
                "pub fn sum_even_squares(nums: &[i32]) -> i32 {\n"
                "    nums.iter()\n"
                "        .copied()\n"
                "        .filter(|n| n % 2 == 0)\n"
                "        .map(|n| n * n)\n"
                "        .sum()\n"
                "}\n"
            ),
        ),
    ),
    Chapter(
        number=14,
        title="More About Cargo and Crates.io",
        summary="Release profiles, `///` doc comments & doctests, `pub use` APIs, Cargo workspaces (`resolver = \"3\"`), and `cargo install`.",
        mental_model=(
            "Cargo scales from a single script to multi-crate monorepos. Workspaces share a single `Cargo.lock` "
            "and `target/` directory across member crates (using `resolver = \"3\"` in Rust 2024). Documentation "
            "comments (`///`) aren't just text—`cargo test` compiles and runs every Rust code block inside them "
            "as a doctest so your docs can never silently rot."
        ),
        key_rules=(
            "`///` documents the following item; `//!` documents the enclosing crate or module.",
            "`cargo test` runs code examples inside `///` comments as doctests automatically.",
            "Workspace root `Cargo.toml` lists `[workspace]` with `members = [...]` and `resolver = \"3\"`.",
            "`cargo yank --vers 1.0.1` prevents new projects from depending on a broken version without breaking existing `Cargo.lock` files.",
            "Any binary named `cargo-foo` on `$PATH` can be invoked as `cargo foo`.",
        ),
        diagram_title="CARGO WORKSPACE LAYOUT",
        diagram=(
            "  my_workspace/\n"
            "   +-- Cargo.toml      ([workspace] resolver = \"3\", members = [...])\n"
            "   +-- Cargo.lock      (ONE shared lockfile for all members)\n"
            "   +-- target/         (ONE shared build cache)\n"
            "   +-- adder/          (binary crate depending on add_one)\n"
            "   +-- add_one/        (library crate)"
        ),
        recall_cards=(
            RecallCard(
                id="ch14_c1",
                chapter=14,
                prompt="What is the difference between `///` and `//!` doc comments?",
                code="//! Crate-level docs\n/// Function-level docs\npub fn add(a: i32, b: i32) -> i32 { a + b }",
                options=(
                    "`///` is for private items; `//!` is for public items",
                    "`///` documents the item that follows it; `//!` documents the enclosing module or crate",
                    "`//!` disables doctests",
                    "They are identical",
                ),
                answer_index=1,
                explanation="Outer doc comments (`///`) attach to the next item; inner doc comments (`//!`) describe the containing crate (`src/lib.rs`) or module.",
            ),
            RecallCard(
                id="ch14_c2",
                chapter=14,
                prompt="Does `cargo yank --vers 0.1.0` delete version 0.1.0 from crates.io?",
                code="$ cargo yank --vers 0.1.0",
                options=(
                    "Yes, it permanently erases the tarball",
                    "No: it blocks new projects from adding 0.1.0 while keeping existing `Cargo.lock` builds working",
                    "Yes, after 24 hours",
                    "It only affects local caches",
                ),
                answer_index=1,
                explanation="Crates.io versions are permanent so existing builds never break; yanking prevents new dependents from picking a broken release.",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch14_cl1",
                chapter=14,
                prompt="Configure the release profile in `Cargo.toml` for maximum optimization level:",
                code_template="[profile.release]\n___ = 3",
                accepted_answers=("opt-level",),
                hint="Cargo profile key controlling LLVM optimization (0..3).",
                explanation="`opt-level = 3` enables full optimizations (default for release; dev defaults to 0).",
            ),
        ),
        clinic=CompilerClinic(
            id="ch14_err",
            chapter=14,
            error_code="DOCTEST",
            title="Stale example inside `///` doc comment",
            broken_code=(
                "/// Adds one.\n"
                "/// ```\n"
                "/// assert_eq!(mycrate::add_one(5), 7);\n"
                "/// ```\n"
                "pub fn add_one(x: i32) -> i32 { x + 1 }"
            ),
            compiler_output=(
                "test src/lib.rs - add_one (line 2) ... FAILED\n"
                "assertion `left == right` failed\n"
                "  left: 6\n"
                " right: 7"
            ),
            question="Why did `cargo test` fail even though there is no `#[test]` function?",
            options=(
                "`cargo test` compiles and executes Rust code blocks inside `///` doc comments as doctests",
                "Comments are compiled as regular code in Rust",
                "`add_one` must be private",
                "Doc comments require `#[cfg(doc)]`",
            ),
            answer_index=0,
            fix_code="/// ```\n/// assert_eq!(mycrate::add_one(5), 6);\n/// ```",
            mental_model="Rust treats doc examples as executable tests—keeping documentation and implementation permanently in sync.",
        ),
        feynman=FeynmanPrompt(
            chapter=14,
            question="Why do Cargo workspaces share a single `Cargo.lock` and `target/` directory across all member crates?",
            rubric_points=(
                "A shared `Cargo.lock` guarantees every crate in the workspace compiles against the exact same dependency versions.",
                "A shared `target/` avoids recompiling common dependencies multiple times.",
                "It speeds up builds and prevents subtle version-mismatch type errors between workspace crates.",
            ),
            key_terms=("Cargo.lock", "target", "version", "shared", "recompile"),
            model_answer=(
                "Sharing one `Cargo.lock` guarantees all workspace crates use identical dependency versions (preventing "
                "duplicate-type conflicts), and sharing `target/` ensures common dependencies are compiled once."
            ),
        ),
    ),
]

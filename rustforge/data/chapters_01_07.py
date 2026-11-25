"""Chapters 1 to 7 of The Rust Programming Language (2024 Edition)."""

from __future__ import annotations

from rustforge.data.models import (
    Chapter,
    ClozeDrill,
    CodingLab,
    CompilerClinic,
    FeynmanPrompt,
    RecallCard,
)

CHAPTERS_01_07: list[Chapter] = [
    Chapter(
        number=1,
        title="Getting Started: rustup, rustc & Cargo",
        summary="Toolchain architecture, ahead-of-time compilation, and Cargo project workflow.",
        mental_model=(
            "Rust is ahead-of-time compiled: `rustc` turns `.rs` source into a standalone native binary "
            "that runs without a runtime or interpreter. `rustup` manages compiler versions and targets, "
            "while `cargo` orchestrates builds, dependency resolution (`Cargo.toml` + `Cargo.lock`), "
            "fast type-checking (`cargo check`), tests, and release optimization."
        ),
        key_rules=(
            "Use `cargo check` during tight edit loops: it runs the borrow checker and type checker without emitting a binary.",
            "`cargo build` produces an unoptimized debug binary in `target/debug/`; `cargo build --release` enables LLVM optimizations in `target/release/`.",
            "Binary crates commit `Cargo.lock` for reproducible builds; library crates let downstream consumers resolve versions.",
            "Rust 2024 Edition is declared in `Cargo.toml` with `edition = \"2024\"`.",
            "Macros end with `!` (such as `println!`) and expand to Rust code at compile time.",
        ),
        diagram_title="RUST TOOLCHAIN PIPELINE",
        diagram=(
            "  src/main.rs + Cargo.toml\n"
            "             |\n"
            "      [ cargo check ]  --> Fast type & borrow check (no binary)\n"
            "             |\n"
            "      [ cargo build ]  --> rustc + LLVM --> target/debug/app\n"
            "             |\n"
            "  [ cargo build --release ] --> LLVM -O3 --> target/release/app"
        ),
        recall_cards=(
            RecallCard(
                id="ch01_c1",
                chapter=1,
                prompt="You edited 3 files and want the fastest feedback on type and borrow errors without running the program. Which Cargo command should you run?",
                code="$ cargo ___",
                options=("cargo run --release", "cargo check", "cargo doc", "cargo publish --dry-run"),
                answer_index=1,
                explanation="`cargo check` skips code generation (LLVM backend) and only runs parsing, macro expansion, type checking, and borrow checking, making it much faster than `cargo build`.",
            ),
            RecallCard(
                id="ch01_c2",
                chapter=1,
                prompt="Why does `println!(\"hello\")` have an exclamation mark `!`?",
                code='fn main() {\n    println!("hello");\n}',
                options=(
                    "It marks a function that can panic",
                    "It invokes a Rust macro rather than a regular function",
                    "It forces synchronous stdout flushing",
                    "It denotes an unsafe FFI call",
                ),
                answer_index=1,
                explanation="The `!` signals a macro invocation. Macros can take variable numbers of arguments and validate format strings at compile time.",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch01_cl1",
                chapter=1,
                prompt="Compile an optimized production binary with Cargo:",
                code_template="cargo build ___",
                accepted_answers=("--release", "-r"),
                hint="Flag that enables release profile optimizations.",
                explanation="`cargo build --release` (or `-r`) compiles with optimizations into `target/release/`.",
            ),
        ),
        clinic=CompilerClinic(
            id="ch01_err",
            chapter=1,
            error_code="E0423",
            title="Calling a macro without `!`",
            broken_code='fn main() {\n    println("Hello, Rust 2024!");\n}',
            compiler_output=(
                "error[E0423]: expected function, found macro `println`\n"
                " --> src/main.rs:2:5\n"
                "  |\n"
                "2 |     println(\"Hello, Rust 2024!\");\n"
                "  |     ^^^^^^^ not a function\n"
                "help: use `!` to invoke the macro: `println!`"
            ),
            question="Why did rustc reject `println(...)`?",
            options=(
                "println is a macro and must be invoked with `!`",
                "println requires `use std::io::println;` first",
                "String literals must be wrapped in `String::from`",
                "main must return `Result` to print",
            ),
            answer_index=0,
            fix_code='fn main() {\n    println!("Hello, Rust 2024!");\n}',
            mental_model="Functions have fixed signatures; `println!` is a macro that parses the format string at compile time and checks every placeholder's type.",
        ),
        feynman=FeynmanPrompt(
            chapter=1,
            question="Explain to a beginner the difference between `rustup`, `rustc`, and `cargo`, and why `cargo check` is faster than `cargo build`.",
            rubric_points=(
                "rustup installs and switches Rust compiler toolchains and targets.",
                "rustc is the compiler itself that turns .rs files into native machine code.",
                "cargo is the build system and package manager (dependencies, builds, tests).",
                "cargo check skips binary/machine-code generation while still verifying types and borrow rules.",
            ),
            key_terms=("rustup", "rustc", "cargo", "check", "binary", "compile"),
            model_answer=(
                "`rustup` manages your installed Rust versions, `rustc` compiles Rust code into a native executable, "
                "and `cargo` manages dependencies, builds, and tests. `cargo check` is faster because it verifies "
                "syntax, types, and borrowing without spending time generating an executable binary."
            ),
        ),
    ),
    Chapter(
        number=2,
        title="Programming a Guessing Game",
        summary="Reading stdin, Result handling, crates (`rand`), `Ordering` with `match`, and variable shadowing.",
        mental_model=(
            "Rust forces you to handle failure and type conversions explicitly right where they happen. "
            "Reading input mutates a `String` buffer via `&mut guess`, parsing returns a `Result` that you "
            "match on (`Ok`/`Err`), and comparing values returns an `Ordering` enum (`Less`, `Greater`, `Equal`) "
            "that `match` forces you to handle exhaustively."
        ),
        key_rules=(
            "References are immutable by default; you must write `&mut guess` (not `&guess`) to let `read_line` mutate the buffer.",
            "Variable shadowing (`let guess: u32 = ...`) lets you reuse a name with a new type after parsing.",
            "`expect()` unwraps `Ok(val)` or panics with your message on `Err`; prefer `match` when recovering from bad user input.",
            "Traits must be in scope to call their methods (e.g., `use rand::Rng;` or `rand::random_range` in `rand` 0.10).",
        ),
        diagram_title="INPUT -> PARSE -> COMPARE FLOW",
        diagram=(
            "  stdin --> read_line(&mut guess: String)\n"
            "               |\n"
            "         guess.trim().parse::<u32>()\n"
            "          /                       \\\n"
            "      Ok(num)                   Err(_)\n"
            "         |                         |\n"
            "  num.cmp(&secret)             continue loop\n"
            "   /     |      \\\n"
            " Less  Equal  Greater"
        ),
        recall_cards=(
            RecallCard(
                id="ch02_c1",
                chapter=2,
                prompt="What happens if you pass `&guess` instead of `&mut guess` to `io::stdin().read_line(&guess)`?",
                code="let mut guess = String::new();\nio::stdin().read_line(&guess).expect(\"failed\");",
                options=(
                    "It compiles because `guess` was declared `mut`",
                    "Compile error: `&guess` is an immutable reference, but `read_line` requires `&mut String`",
                    "It compiles but leaves `guess` empty at runtime",
                    "It panics at runtime",
                ),
                answer_index=1,
                explanation="Declaring `let mut guess` allows mutable borrows, but each reference itself is immutable unless explicitly written `&mut guess`.",
            ),
            RecallCard(
                id="ch02_c2",
                chapter=2,
                prompt="Why does Rust allow `let guess: u32 = guess.trim().parse().expect(...);` when `guess` is already a `String`?",
                code='let guess = String::from("42");\nlet guess: u32 = guess.trim().parse().unwrap();',
                options=(
                    "Rust variables are dynamically typed",
                    "Shadowing creates a brand-new variable binding with the same name and a new type",
                    "String automatically coerces to u32",
                    "Only `mut` variables can change type",
                ),
                answer_index=1,
                explanation="Shadowing via `let` binds a new variable that obscures the previous one, letting you transform types cleanly without inventing names like `guess_str` and `guess_num`.",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch02_cl1",
                chapter=2,
                prompt="Handle a `parse()` Result by skipping invalid input in a loop:",
                code_template="let guess: u32 = match guess.trim().parse() {\n    Ok(num) => num,\n    ___ => continue,\n};",
                accepted_answers=("Err(_)", "Err(_e)"),
                hint="Match the error variant while ignoring its inner value.",
                explanation="`Err(_) => continue` catches any parse failure cleanly without crashing the program.",
            ),
        ),
        clinic=CompilerClinic(
            id="ch02_err",
            chapter=2,
            error_code="E0308",
            title="Mismatched types in `cmp`",
            broken_code=(
                "use std::cmp::Ordering;\n"
                "fn check(guess: String, secret: u32) {\n"
                "    match guess.cmp(&secret) {\n"
                "        Ordering::Equal => println!(\"win\"),\n"
                "        _ => {}\n"
                "    }\n"
                "}"
            ),
            compiler_output=(
                "error[E0308]: mismatched types\n"
                " --> src/main.rs:3:21\n"
                "  |\n"
                "3 |     match guess.cmp(&secret) {\n"
                "  |                 --- ^^^^^^^ expected `&String`, found `&u32`"
            ),
            question="How should you fix this type mismatch?",
            options=(
                "Parse `guess` into a `u32` (shadowing it) before calling `.cmp(&secret)`",
                "Cast `&secret as &String`",
                "Use `==` instead of `cmp` because `==` coerces String to u32",
                "Add `mut` to `secret`",
            ),
            answer_index=0,
            fix_code=(
                "let guess: u32 = guess.trim().parse().expect(\"number\");\n"
                "match guess.cmp(&secret) { ... }"
            ),
            mental_model="Rust has strong static typing with no implicit string-to-number coercion. Convert explicitly and handle the `Result`.",
        ),
        feynman=FeynmanPrompt(
            chapter=2,
            question="Why does `read_line` return a `Result` instead of just returning the number of bytes directly?",
            rubric_points=(
                "I/O can fail at runtime (e.g., invalid UTF-8 or closed stdin).",
                "Result<T, E> is an enum with Ok and Err variants.",
                "Returning Result forces the caller to acknowledge potential failure at compile time (unused Result triggers a warning).",
            ),
            key_terms=("Result", "Ok", "Err", "fail", "compile", "handle"),
            model_answer=(
                "I/O operations can fail for reasons outside the program's control. Wrapping the outcome in "
                "`Result<usize, io::Error>` encodes success (`Ok`) and failure (`Err`) in the type system so you "
                "cannot silently ignore errors."
            ),
        ),
    ),
    Chapter(
        number=3,
        title="Common Programming Concepts",
        summary="Mutability, constants, shadowing, scalar & compound types, overflow modes, statements vs. expressions, and control flow.",
        mental_model=(
            "Rust is an expression-based language: almost everything (`if`, `match`, blocks `{ ... }`, even `loop` "
            "with `break value`) evaluates to a value. Adding a semicolon turns an expression into a statement that "
            "evaluates to the unit type `()`. Variables are immutable by default so mutability is always an explicit signal."
        ),
        key_rules=(
            "`const` requires a type annotation and a compile-time constant expression; it can never be `mut`.",
            "Shadowing (`let x = ...`) can change a variable's type; mutating (`mut x`) cannot.",
            "Integer overflow panics in debug builds and wraps (two's complement) in release builds. Use `wrapping_*`, `checked_*`, `overflowing_*`, or `saturating_*` to be explicit.",
            "Arrays `[T; N]` have fixed length on the stack; out-of-bounds indexing panics safely instead of reading invalid memory.",
            "A block's final expression WITHOUT a trailing semicolon is its return value.",
        ),
        diagram_title="STATEMENT VS. EXPRESSION",
        diagram=(
            "  let y = {\n"
            "      let x = 3;   <-- Statement (ends with ';', returns ())\n"
            "      x + 1        <-- Expression (NO ';', returns 4 to y)\n"
            "  };\n"
            "  // y == 4  |  If you wrote `x + 1;`, y would be ()!"
        ),
        recall_cards=(
            RecallCard(
                id="ch03_c1",
                chapter=3,
                prompt="Will this function compile? Predict before checking:",
                code="fn plus_one(x: i32) -> i32 {\n    x + 1;\n}",
                options=(
                    "Yes, it returns x + 1",
                    "No: the semicolon makes the body evaluate to `()`, mismatched with `-> i32`",
                    "Yes, Rust ignores trailing semicolons on the last line",
                    "It compiles with a warning and returns 0",
                ),
                answer_index=1,
                explanation="Adding `;` turns `x + 1` from an expression into a statement, so the function implicitly returns `()` instead of `i32` (E0308).",
            ),
            RecallCard(
                id="ch03_c2",
                chapter=3,
                prompt="What happens if `let x: u8 = 255; let y = x + 1;` runs in `--release` mode vs debug mode?",
                code="let x: u8 = 255;\nlet y = x + 1;",
                options=(
                    "Panics in both debug and release",
                    "Panics in debug mode; wraps to 0 (two's complement) in release mode",
                    "Wraps to 0 in debug mode; panics in release mode",
                    "Automatically promotes y to u16",
                ),
                answer_index=1,
                explanation="Rust checks overflow in debug builds (panicking) and omits the check in release builds (two's complement wrapping). Never rely on implicit wrapping; use `checked_add`, `saturating_add`, or `wrapping_add`.",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch03_cl1",
                chapter=3,
                prompt="Return a value from an infinite `loop` when `counter == 10`:",
                code_template="let result = loop {\n    counter += 1;\n    if counter == 10 {\n        ___ counter * 2;\n    }\n};",
                accepted_answers=("break",),
                hint="Keyword that exits a loop and yields a value.",
                explanation="`break expr;` exits the loop and evaluates the `loop` expression to `expr`.",
            ),
        ),
        clinic=CompilerClinic(
            id="ch03_err",
            chapter=3,
            error_code="E0308",
            title="Incompatible `if`/`else` branch types",
            broken_code='let cond = true;\nlet number = if cond { 5 } else { "six" };',
            compiler_output=(
                "error[E0308]: `if` and `else` have incompatible types\n"
                " --> src/main.rs:2:35\n"
                "  |\n"
                '2 | let number = if cond { 5 } else { "six" };\n'
                "  |                        -          ^^^^^ expected integer, found `&str`"
            ),
            question="Why does Rust reject this `if` expression?",
            options=(
                "Every branch of an `if` expression must evaluate to the exact same static type",
                "`if` cannot be used on the right-hand side of `let`",
                "`cond` must be wrapped in parentheses",
                "String literals cannot appear inside `else`",
            ),
            answer_index=0,
            fix_code="let cond = true;\nlet number = if cond { 5 } else { 6 };",
            mental_model="Because Rust determines every variable's type at compile time, all arms of an `if` or `match` expression must unify to a single type.",
        ),
        feynman=FeynmanPrompt(
            chapter=3,
            question="Explain the difference between mutability (`let mut x`) and shadowing (`let x = ...`) in Rust.",
            rubric_points=(
                "`let mut x` keeps the same variable and memory slot and must keep the same type.",
                "Shadowing creates a brand-new variable binding with `let`, which can have a different type.",
                "After shadowing, the new variable is immutable again unless marked `mut`.",
            ),
            key_terms=("mut", "shadow", "type", "new variable", "immutable"),
            model_answer=(
                "`let mut x` lets you overwrite the value inside the same variable, so its type can never change. "
                "Shadowing with a second `let x = ...` creates a brand-new variable that hides the old one, allowing "
                "you to change its type while keeping the final value immutable."
            ),
        ),
        lab=CodingLab(
            id="lab_ch03_fib",
            chapter=3,
            title="Iterative Fibonacci & Safe Overflow",
            objective="Implement `fib(n: u32) -> Option<u64>` using `checked_add` so overflow returns `None` instead of panicking or wrapping.",
            starter_code=(
                "pub fn fib(n: u32) -> Option<u64> {\n"
                "    // TODO: Return Some(nth Fibonacci number), or None on u64 overflow.\n"
                "    // fib(0) = Some(0), fib(1) = Some(1), fib(10) = Some(55)\n"
                "    todo!()\n"
                "}\n\n"
                "#[cfg(test)]\n"
                "mod tests {\n"
                "    use super::*;\n"
                "    #[test]\n"
                "    fn base_and_small() {\n"
                "        assert_eq!(fib(0), Some(0));\n"
                "        assert_eq!(fib(1), Some(1));\n"
                "        assert_eq!(fib(10), Some(55));\n"
                "    }\n"
                "    #[test]\n"
                "    fn detects_overflow() {\n"
                "        assert_eq!(fib(93), Some(12200160415121876738));\n"
                "        assert_eq!(fib(94), None);\n"
                "    }\n"
                "}\n"
            ),
            solution_code=(
                "pub fn fib(n: u32) -> Option<u64> {\n"
                "    let (mut a, mut b) = (0u64, 1u64);\n"
                "    for _ in 0..n {\n"
                "        let next = a.checked_add(b)?;\n"
                "        a = b;\n"
                "        b = next;\n"
                "    }\n"
                "    Some(a)\n"
                "}\n"
            ),
        ),
    ),
    Chapter(
        number=4,
        title="Understanding Ownership, Borrowing & Slices",
        summary="Stack vs. heap, move semantics, Copy vs. Drop, references, the aliasing XOR mutability law, and slices.",
        mental_model=(
            "Ownership eliminates garbage collection and manual `free()` bugs with three compile-time rules: "
            "(1) every value has one owner, (2) there can only be one owner at a time, and (3) when the owner "
            "leaves scope, the value is dropped. Borrowing lets you lend access via references under the golden law: "
            "at any point, you may have EITHER any number of immutable references (`&T`) OR exactly one mutable "
            "reference (`&mut T`), never both, and references must always be valid."
        ),
        key_rules=(
            "Heap types like `String` and `Vec<T>` MOVE on assignment (copying ptr/len/cap on stack and invalidating the old variable) to prevent double-free.",
            "Stack-only types that implement `Copy` (integers, `bool`, `char`, `f64`, tuples of `Copy` types) are bitwise copied and remain valid.",
            "A type cannot implement both `Copy` and `Drop`.",
            "Non-Lexical Lifetimes (NLL): a reference's scope ends at its LAST USE, not necessarily the closing `}`.",
            "Slices (`&str`, `&[T]`) are fat pointers `(ptr, len)` tied by the borrow checker to the underlying owner.",
        ),
        diagram_title="STRING MOVE VS. BORROW (STACK & HEAP)",
        diagram=(
            "  MOVE: let s2 = s1;                HEAP\n"
            "  s1 [INVALIDATED]                  +---+---+---+---+---+\n"
            "  s2 [ptr | len:5 | cap:5] -------> | h | e | l | l | o |\n"
            "                                    +---+---+---+---+---+\n"
            "  BORROW: let r = &s2;\n"
            "  r  [ptr to s2] ---> s2 ---> HEAP  (r does NOT own or drop heap)"
        ),
        recall_cards=(
            RecallCard(
                id="ch04_c1",
                chapter=4,
                prompt="Will this code compile under Rust's Non-Lexical Lifetimes (NLL)?",
                code=(
                    'let mut s = String::from("hello");\n'
                    "let r1 = &s;\n"
                    "let r2 = &s;\n"
                    'println!("{r1} and {r2}");\n'
                    "let r3 = &mut s;\n"
                    'println!("{r3}");'
                ),
                options=(
                    "No: r1 and r2 are still in scope until the end of the block",
                    "Yes: r1 and r2 are last used in the first println!, so r3 does not overlap them",
                    "No: you can never borrow `s` mutably after borrowing it immutably",
                    "Yes, but it panics at runtime",
                ),
                answer_index=1,
                explanation="Under NLL, a reference's lifetime ends at its last usage. Because `r1` and `r2` are never used after the first `println!`, `r3 = &mut s` does not conflict.",
            ),
            RecallCard(
                id="ch04_c2",
                chapter=4,
                prompt="What is the bug if a function tries to return `&String` pointing to a local `String` created inside the function?",
                code='fn dangle() -> &String {\n    let s = String::from("hi");\n    &s\n}',
                options=(
                    "Memory leak",
                    "Dangling reference: `s` is dropped at the end of `dangle`, leaving `&s` pointing to freed memory",
                    "Stack overflow",
                    "Double free",
                ),
                answer_index=1,
                explanation="When `dangle` exits, `s` is dropped. Returning `&s` would create a dangling pointer. Fix: return the owned `String` directly (`-> String`).",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch04_cl1",
                chapter=4,
                prompt="Accept both `&String` and string literals (`&str`) idiomatically via deref coercion:",
                code_template="fn first_word(s: ___) -> &str {\n    s.split_whitespace().next().unwrap_or(\"\")\n}",
                accepted_answers=("&str",),
                hint="Use the string slice type rather than `&String`.",
                explanation="Taking `&str` works with both string literals and `&String` (via `Deref` coercion).",
            ),
        ),
        clinic=CompilerClinic(
            id="ch04_err",
            chapter=4,
            error_code="E0382",
            title="Borrow of moved value",
            broken_code=(
                'fn main() {\n'
                '    let s1 = String::from("rust");\n'
                '    let s2 = s1;\n'
                '    println!("{s1}");\n'
                '}'
            ),
            compiler_output=(
                "error[E0382]: borrow of moved value: `s1`\n"
                " --> src/main.rs:4:15\n"
                "  |\n"
                '2 |     let s1 = String::from("rust");\n'
                "  |         -- move occurs because `s1` has type `String`, which does not implement `Copy`\n"
                "3 |     let s2 = s1;\n"
                "  |              -- value moved here\n"
                '4 |     println!("{s1}");\n'
                "  |               ^^^^ value borrowed here after move"
            ),
            question="Which fix avoids copying heap memory while letting you print both?",
            options=(
                "Borrow `s1` with `let s2 = &s1;` instead of moving ownership",
                "Add `mut` to `s1`",
                "Use `let s2 = *s1;`",
                "Wrap `println!` in `unsafe`",
            ),
            answer_index=0,
            fix_code='let s1 = String::from("rust");\nlet s2 = &s1;\nprintln!("{s1} / {s2}");',
            mental_model="Assigning a non-Copy value moves ownership. Use `&s1` when you only need read access, or `s1.clone()` when you genuinely need two independent heap buffers.",
        ),
        feynman=FeynmanPrompt(
            chapter=4,
            question="Explain Rust's aliasing XOR mutability rule (`&T` vs `&mut T`) and what bugs it prevents at compile time.",
            rubric_points=(
                "You can have many immutable references (&T) OR one mutable reference (&mut T) at the same time, never both.",
                "Prevents data races (concurrent read/write or write/write without synchronization).",
                "Prevents iterator invalidation / dangling pointers (e.g., resizing a Vec while holding a slice/reference into it).",
            ),
            key_terms=("mutable", "immutable", "data race", "dangling", "one", "borrows"),
            model_answer=(
                "Rust forbids simultaneous aliasing and mutation: either many readers (`&T`) or one exclusive writer "
                "(`&mut T`). That single rule prevents data races across threads and iterator/slice invalidation "
                "(like reallocating a `Vec` while another reference still points to its old buffer) at compile time."
            ),
        ),
        lab=CodingLab(
            id="lab_ch04_slice",
            chapter=4,
            title="Zero-Copy First Word Slice",
            objective="Implement `first_word(s: &str) -> &str` returning the first space-delimited word without allocating a `String`.",
            starter_code=(
                "pub fn first_word(s: &str) -> &str {\n"
                "    // TODO: Return a slice of the first word (trimmed of leading spaces).\n"
                "    // Do not allocate a String.\n"
                "    todo!()\n"
                "}\n\n"
                "#[cfg(test)]\n"
                "mod tests {\n"
                "    use super::*;\n"
                "    #[test]\n"
                "    fn finds_first_word() {\n"
                '        assert_eq!(first_word("hello world"), "hello");\n'
                '        assert_eq!(first_word("rust"), "rust");\n'
                '        assert_eq!(first_word("   leading spaces"), "leading");\n'
                '        assert_eq!(first_word(""), "");\n'
                "    }\n"
                "}\n"
            ),
            solution_code=(
                "pub fn first_word(s: &str) -> &str {\n"
                "    let trimmed = s.trim_start();\n"
                "    for (i, byte) in trimmed.bytes().enumerate() {\n"
                "        if byte == b' ' {\n"
                "            return &trimmed[..i];\n"
                "        }\n"
                "    }\n"
                "    trimmed\n"
                "}\n"
            ),
        ),
    ),
    Chapter(
        number=5,
        title="Using Structs to Structure Related Data",
        summary="Named structs, tuple structs, unit-like structs, struct update syntax, Debug/dbg!, and impl methods.",
        mental_model=(
            "Structs bundle related fields into a single owned type, and `impl` blocks attach behavior directly "
            "to that type. Notice that struct update syntax (`..user1`) acts like assignment: it MOVES non-Copy "
            "fields out of `user1` while copying `Copy` fields. Method calls use automatic referencing and "
            "dereferencing so `rect.area()` works cleanly whether `rect` is `Rect`, `&Rect`, or `&mut Rect`."
        ),
        key_rules=(
            "Mutability is a property of the whole struct binding (`let mut u`), not individual fields.",
            "Struct update syntax `User { email: new_email, ..user1 }` moves any non-Copy fields taken from `user1`.",
            "Methods take `&self`, `&mut self`, or `self` (consuming ownership); associated functions (like `Self::new`) omit `self`.",
            "`dbg!(&expr)` prints file, line, expression, and `Debug` value to stderr and returns ownership of the expression.",
        ),
        diagram_title="METHOD RECEIVER OWNERSHIP",
        diagram=(
            "  impl Rect {\n"
            "      fn area(&self) -> u32          // Borrows immutably (read)\n"
            "      fn scale(&mut self, k: u32)    // Borrows mutably (edit)\n"
            "      fn into_box(self) -> Box<Self> // Consumes self (move)\n"
            "      fn square(n: u32) -> Self      // Associated fn (Rect::square)\n"
            "  }"
        ),
        recall_cards=(
            RecallCard(
                id="ch05_c1",
                chapter=5,
                prompt="After `let u2 = User { email: String::from(\"b@x\"), ..u1 };`, can you still use `u1.username` (a `String`) and `u1.active` (a `bool`)?",
                code=(
                    "struct User { active: bool, username: String, email: String }\n"
                    "let u2 = User { email: String::from(\"b@x\"), ..u1 };"
                ),
                options=(
                    "Neither can be used; all of u1 is moved",
                    "`u1.active` is still valid (`Copy`), but `u1.username` was moved into `u2`",
                    "Both are still valid because `..u1` clones fields",
                    "`u1.username` is valid because `email` was replaced",
                ),
                answer_index=1,
                explanation="Struct update syntax moves non-Copy fields that weren't explicitly replaced (`username`), while `active` (`bool`) is `Copy` so `u1.active` remains usable.",
            ),
            RecallCard(
                id="ch05_c2",
                chapter=5,
                prompt="Why does `dbg!(30 * scale)` work inside a struct initializer without stealing ownership away from the field?",
                code="let rect = Rectangle { width: dbg!(30 * scale), height: 50 };",
                options=(
                    "dbg! takes a reference implicitly",
                    "dbg! takes ownership of the expression, prints it to stderr, and returns ownership back",
                    "dbg! only accepts Copy types",
                    "dbg! is removed at compile time",
                ),
                answer_index=1,
                explanation="`dbg!` takes ownership, prints `[file:line] expr = value` to stderr, and returns ownership of the value. Pass `dbg!(&val)` if you don't want to move `val`.",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch05_cl1",
                chapter=5,
                prompt="Enable `{:?}` and `{:#?}` debug printing on a struct automatically:",
                code_template="___\nstruct Rectangle {\n    width: u32,\n    height: u32,\n}",
                accepted_answers=("#[derive(Debug)]",),
                hint="Outer attribute that derives the Debug trait.",
                explanation="`#[derive(Debug)]` generates the `std::fmt::Debug` implementation at compile time.",
            ),
        ),
        clinic=CompilerClinic(
            id="ch05_err",
            chapter=5,
            error_code="E0277",
            title="Printing a struct without `Debug`",
            broken_code='struct Point { x: i32, y: i32 }\nfn main() {\n    let p = Point { x: 1, y: 2 };\n    println!("{p:?}");\n}',
            compiler_output=(
                "error[E0277]: `Point` doesn't implement `Debug`\n"
                " --> src/main.rs:4:15\n"
                "  |\n"
                '4 |     println!("{p:?}");\n'
                "  |               ^^^^^ `Point` cannot be formatted using `{:?}`\n"
                "help: consider annotating `Point` with `#[derive(Debug)]`"
            ),
            question="Why doesn't Rust automatically implement `Debug` or `Display` on every struct?",
            options=(
                "Trait implementations are opt-in so types don't leak internal representation or incur compile-time cost unintentionally",
                "Structs can only implement `Display`, never `Debug`",
                "Only tuple structs can be printed",
                "Printing structs requires `unsafe`",
            ),
            answer_index=0,
            fix_code="#[derive(Debug)]\nstruct Point { x: i32, y: i32 }",
            mental_model="Rust keeps trait implementations explicit. Derive `Debug` for developer diagnostics and implement `Display` manually for user-facing formatting.",
        ),
        feynman=FeynmanPrompt(
            chapter=5,
            question="When should a method take `&self`, `&mut self`, or `self` by value?",
            rubric_points=(
                "`&self` for read-only inspection without taking ownership.",
                "`&mut self` when mutating fields in place.",
                "`self` when transforming/consuming the value into something else so the old value cannot be reused.",
            ),
            key_terms=("&self", "&mut self", "self", "read", "mutate", "consume"),
            model_answer=(
                "Use `&self` to read without moving, `&mut self` to modify fields in place, and `self` by value "
                "when the method consumes the struct (such as converting it into another type or closing a resource) "
                "so the caller cannot use the old state afterward."
            ),
        ),
        lab=CodingLab(
            id="lab_ch05_rect",
            chapter=5,
            title="Rectangle Struct & Methods",
            objective="Implement `Rectangle::square`, `area(&self)`, and `can_hold(&self, other: &Rectangle) -> bool`.",
            starter_code=(
                "#[derive(Debug, PartialEq)]\n"
                "pub struct Rectangle {\n"
                "    pub width: u32,\n"
                "    pub height: u32,\n"
                "}\n\n"
                "impl Rectangle {\n"
                "    pub fn square(size: u32) -> Self { todo!() }\n"
                "    pub fn area(&self) -> u32 { todo!() }\n"
                "    pub fn can_hold(&self, other: &Rectangle) -> bool { todo!() }\n"
                "}\n\n"
                "#[cfg(test)]\n"
                "mod tests {\n"
                "    use super::*;\n"
                "    #[test]\n"
                "    fn rect_methods() {\n"
                "        let big = Rectangle::square(10);\n"
                "        let small = Rectangle { width: 8, height: 9 };\n"
                "        assert_eq!(big.area(), 100);\n"
                "        assert!(big.can_hold(&small));\n"
                "        assert!(!small.can_hold(&big));\n"
                "    }\n"
                "}\n"
            ),
            solution_code=(
                "impl Rectangle {\n"
                "    pub fn square(size: u32) -> Self {\n"
                "        Self { width: size, height: size }\n"
                "    }\n"
                "    pub fn area(&self) -> u32 {\n"
                "        self.width * self.height\n"
                "    }\n"
                "    pub fn can_hold(&self, other: &Rectangle) -> bool {\n"
                "        self.width > other.width && self.height > other.height\n"
                "    }\n"
                "}\n"
            ),
        ),
    ),
    Chapter(
        number=6,
        title="Enums and Pattern Matching",
        summary="Algebraic sum types, `Option<T>` instead of null, exhaustive `match`, `if let`, and `let...else`.",
        mental_model=(
            "Rust enums are algebraic sum types: each variant can carry completely different data (unit, tuple, "
            "or struct fields). Because Rust has NO `null`, absence is encoded in `Option<T>` (`Some(T)` | `None`), "
            "and `match` is checked by the compiler for exhaustiveness—meaning you can never forget a case."
        ),
        key_rules=(
            "You cannot add `i8` and `Option<i8>` directly: you must handle `None` first.",
            "`match` arms are checked in order and MUST cover every possible variant (use `_` or a catch-all binding).",
            "Use `if let Some(x) = opt { ... }` when you only care about one pattern and want less boilerplate than `match`.",
            "Use `let Some(x) = opt else { return ...; };` (stabilized & highlighted in Rust 2024) for clean early returns while binding `x` into the outer scope.",
        ),
        diagram_title="OPTION<T> VS NULL",
        diagram=(
            "  Other languages:  x: User  ---> [ User | NULL ]  (surprise crash!)\n"
            "  Rust:             x: User  ---> [ Always valid User ]\n"
            "                    y: Option<User>\n"
            "                       /          \\\n"
            "                 Some(User)       None   <-- compiler forces handling"
        ),
        recall_cards=(
            RecallCard(
                id="ch06_c1",
                chapter=6,
                prompt="What is the advantage of `let Some(val) = maybe else { return None; };` over `if let`?",
                code="fn double(maybe: Option<i32>) -> Option<i32> {\n    let Some(val) = maybe else { return None; };\n    Some(val * 2)\n}",
                options=(
                    "It skips exhaustiveness checking",
                    "It binds `val` directly into the outer scope and diverges on mismatch, avoiding nested indentation",
                    "It clones `maybe` automatically",
                    "It only works with `Option`, not custom enums",
                ),
                answer_index=1,
                explanation="`let...else` keeps the happy path unindented: the `else` block MUST diverge (`return`, `break`, `continue`, or `panic!`), guaranteeing `val` is bound afterward.",
            ),
            RecallCard(
                id="ch06_c2",
                chapter=6,
                prompt="Why does `Option<&T>` take the same number of bytes in memory as `&T`?",
                code="std::mem::size_of::<Option<&i32>>() == std::mem::size_of::<&i32>()",
                options=(
                    "Option is stored on the heap",
                    "Null-pointer optimization: `&T` can never be 0, so Rust uses the 0 bit-pattern to represent `None`",
                    "References are 1 byte in Rust",
                    "It doesn't; Option always adds 8 bytes for a tag",
                ),
                answer_index=1,
                explanation="Because references (`&T`, `Box<T>`, `NonNull<T>`) are guaranteed non-null, Rust packs `None` into the unused zero representation—zero memory overhead!",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch06_cl1",
                chapter=6,
                prompt="Complete the `let...else` statement to return early if `coin` is not a Quarter:",
                code_template="let Coin::Quarter(state) = coin ___ {\n    return None;\n};",
                accepted_answers=("else",),
                hint="Keyword introducing the diverging fallback block.",
                explanation="`let PATTERN = expr else { diverge };` binds pattern variables into the enclosing scope.",
            ),
        ),
        clinic=CompilerClinic(
            id="ch06_err",
            chapter=6,
            error_code="E0004",
            title="Non-exhaustive `match` pattern",
            broken_code=(
                "enum State { Idle, Running, Failed(String) }\n"
                "fn label(s: State) -> &'static str {\n"
                "    match s {\n"
                '        State::Idle => "idle",\n'
                '        State::Running => "running",\n'
                "    }\n"
                "}"
            ),
            compiler_output=(
                "error[E0004]: non-exhaustive patterns: `State::Failed(_)` not covered\n"
                " --> src/main.rs:3:11\n"
                "  |\n"
                "3 |     match s {\n"
                "  |           ^ pattern `State::Failed(_)` not covered"
            ),
            question="Why is E0004 a superpower during refactoring?",
            options=(
                "Whenever you add a new enum variant, rustc flags every `match` across the entire codebase that forgot to handle it",
                "It automatically inserts a default return value",
                "It converts enums into integers",
                "It only triggers in release builds",
            ),
            answer_index=0,
            fix_code='match s {\n    State::Idle => "idle",\n    State::Running => "running",\n    State::Failed(_) => "failed",\n}',
            mental_model="Avoid using `_ => ...` lazily when matching your own domain enums; listing variants explicitly lets the compiler guide every future refactor.",
        ),
        feynman=FeynmanPrompt(
            chapter=6,
            question="Why did Rust eliminate `null` in favor of `Option<T>`?",
            rubric_points=(
                "Null lets any reference silently be absent, causing runtime null-pointer crashes.",
                "Option<T> makes absence part of the static type system (T vs Option<T>).",
                "The compiler forces you to explicitly handle None before using the inner T.",
            ),
            key_terms=("null", "Option", "Some", "None", "compile", "type"),
            model_answer=(
                "In languages with `null`, every value might secretly be missing, leading to runtime crashes. "
                "Rust encodes presence vs. absence in the type `Option<T>` (`Some(T)` or `None`), so a plain `T` "
                "is guaranteed non-null and the compiler forces you to handle `None` explicitly."
            ),
        ),
        lab=CodingLab(
            id="lab_ch06_eval",
            chapter=6,
            title="Safe Expression Evaluator Enum",
            objective="Implement `eval(op: Op) -> Option<i32>` handling `Add`, `Sub`, `Mul`, and `Div` (returning `None` on division by zero).",
            starter_code=(
                "pub enum Op {\n"
                "    Add(i32, i32),\n"
                "    Sub(i32, i32),\n"
                "    Mul(i32, i32),\n"
                "    Div(i32, i32),\n"
                "}\n\n"
                "pub fn eval(op: Op) -> Option<i32> {\n"
                "    todo!()\n"
                "}\n\n"
                "#[cfg(test)]\n"
                "mod tests {\n"
                "    use super::*;\n"
                "    #[test]\n"
                "    fn evaluates_ops() {\n"
                "        assert_eq!(eval(Op::Add(2, 3)), Some(5));\n"
                "        assert_eq!(eval(Op::Sub(10, 4)), Some(6));\n"
                "        assert_eq!(eval(Op::Mul(3, 7)), Some(21));\n"
                "        assert_eq!(eval(Op::Div(10, 2)), Some(5));\n"
                "        assert_eq!(eval(Op::Div(10, 0)), None);\n"
                "    }\n"
                "}\n"
            ),
            solution_code=(
                "pub fn eval(op: Op) -> Option<i32> {\n"
                "    match op {\n"
                "        Op::Add(a, b) => a.checked_add(b),\n"
                "        Op::Sub(a, b) => a.checked_sub(b),\n"
                "        Op::Mul(a, b) => a.checked_mul(b),\n"
                "        Op::Div(_, 0) => None,\n"
                "        Op::Div(a, b) => a.checked_div(b),\n"
                "    }\n"
                "}\n"
            ),
        ),
    ),
    Chapter(
        number=7,
        title="Packages, Crates, and Modules",
        summary="Module tree, privacy boundaries, `crate`/`super`/`self`, `pub use` re-exports, and file layout.",
        mental_model=(
            "A package (`Cargo.toml`) holds up to one library crate (`src/lib.rs`) and any number of binary crates "
            "(`src/main.rs`, `src/bin/*.rs`). Inside a crate, `mod foo;` tells the compiler to include `src/foo.rs` "
            "(or `src/foo/mod.rs`) into the module tree. Everything is PRIVATE by default: child modules can see "
            "their ancestors' private items, but parents cannot see inside private child modules."
        ),
        key_rules=(
            "Making a `struct` `pub` keeps its fields private unless each field is marked `pub`; making an `enum` `pub` makes ALL its variants public.",
            "Idiomatic `use`: bring functions in via their parent module (`hosting::add()`), but bring structs/enums in directly (`use std::collections::HashMap;`).",
            "`pub use` re-exports an item so external users get a clean public API regardless of internal file layout.",
            "Declare each file with `mod name;` ONCE in the crate tree; other files reference it via `crate::name` or `super::name`.",
        ),
        diagram_title="CRATE MODULE TREE & PRIVACY",
        diagram=(
            "  crate (src/lib.rs)\n"
            "   +-- pub mod front_of_house  (src/front_of_house.rs)\n"
            "   |    +-- pub mod hosting    (src/front_of_house/hosting.rs)\n"
            "   |         +-- pub fn add_to_waitlist()\n"
            "   +-- mod back_of_house       [private: siblings can access,\n"
            "        +-- fn fix_order()      external crates cannot]"
        ),
        recall_cards=(
            RecallCard(
                id="ch07_c1",
                chapter=7,
                prompt="You mark `pub struct Breakfast { pub toast: String, fruit: String }` and `pub enum Appetizer { Soup, Salad }`. What can external callers access?",
                code="pub struct Breakfast { pub toast: String, fruit: String }\npub enum Appetizer { Soup, Salad }",
                options=(
                    "All fields of Breakfast and all variants of Appetizer",
                    "`Breakfast.toast` and all variants of `Appetizer`, but NOT `Breakfast.fruit`",
                    "Only `Breakfast.toast`; `Appetizer` variants need `pub` too",
                    "Nothing without a `pub mod`",
                ),
                answer_index=1,
                explanation="Struct fields stay private by default even on a `pub struct`, whereas all variants of a `pub enum` are automatically public.",
            ),
            RecallCard(
                id="ch07_c2",
                chapter=7,
                prompt="What does `pub use crate::front_of_house::hosting;` achieve?",
                code="pub use crate::front_of_house::hosting;",
                options=(
                    "Makes every private function inside `hosting` public",
                    "Re-exports `hosting` at the current module path so external callers can access it directly",
                    "Copies the compiled code of `hosting` twice",
                    "Imports `hosting` only for tests",
                ),
                answer_index=1,
                explanation="`pub use` re-exports an item, letting you decouple your internal module hierarchy from the clean public API presented to users.",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch07_cl1",
                chapter=7,
                prompt="Call a function defined in the parent module using a relative path:",
                code_template="mod child {\n    fn run() {\n        ___::parent_helper();\n    }\n}",
                accepted_answers=("super",),
                hint="Keyword analogous to `..` in filesystem paths.",
                explanation="`super::` starts a relative path from the parent module.",
            ),
        ),
        clinic=CompilerClinic(
            id="ch07_err",
            chapter=7,
            error_code="E0603",
            title="Private function in a public module",
            broken_code=(
                "mod auth {\n"
                "    fn verify() -> bool { true }\n"
                "}\n"
                "fn main() { auth::verify(); }"
            ),
            compiler_output=(
                "error[E0603]: function `verify` is private\n"
                " --> src/main.rs:4:19\n"
                "  |\n"
                "4 | fn main() { auth::verify(); }\n"
                "  |                   ^^^^^^ private function"
            ),
            question="Why could `main` see `auth`, yet fail to call `auth::verify()`?",
            options=(
                "`auth` is a sibling of `main` (so `main` can see `auth`), but items INSIDE `auth` are private unless marked `pub`",
                "`main` must be inside `mod auth`",
                "`verify` needs to return `()`",
                "`mod auth` must be in a separate file",
            ),
            answer_index=0,
            fix_code="mod auth {\n    pub fn verify() -> bool { true }\n}",
            mental_model="Siblings can see each other, and children can see ancestors, but crossing INTO a child module requires `pub` on the target item.",
        ),
        feynman=FeynmanPrompt(
            chapter=7,
            question="Explain why you declare `mod foo;` only once in a crate instead of writing `mod foo;` in every file that needs `foo`.",
            rubric_points=(
                "`mod foo;` defines and compiles the module into the module tree at that location.",
                "Writing `mod foo;` in two places compiles the file twice as two separate modules.",
                "Other files should import from the already-declared module via `use crate::foo::...`.",
            ),
            key_terms=("mod", "tree", "once", "use", "crate"),
            model_answer=(
                "`mod foo;` is a declaration that mounts `foo.rs` into the crate's module tree—it is NOT like C's `#include`. "
                "You declare `mod foo;` once in its parent module, and every other file references it with `use crate::foo::...`."
            ),
        ),
    ),
]

# RustForge CLI

A zero-dependency, neuroscience-backed terminal mastery trainer covering **all 21 chapters and Appendices A–G** of *The Rust Programming Language* (**Rust 2024 Edition**).

Designed for crisp, distraction-free terminal workflows (including narrow mobile terminals, cloud `code-server` containers, Linux, macOS, and Windows), with monochrome high-contrast styling and optional Bionic Reading fixation anchors for prose.

---

## The Story: 02:14 AM vs. The Borrow Checker

Every Rust developer remembers the night the compiler finally broke them.

Mine started at 02:14 AM in a cramped terminal window. I had read Chapters 1 through 10 of *The Rust Programming Language* twice, nodded along to every paragraph about ownership, and felt completely ready to build something real. Ten minutes later, `rustc` hit me with a wall of red: `E0382: borrow of moved value`, followed by `E0502: cannot borrow as mutable because it is also borrowed as immutable`, followed by a lifetime error that made `'a` look like an ancient curse.

Reading had given me the *illusion* of fluency—not the reflex.

Passive rereading feels productive while your eyes glide over clean code, yet a week later your brain retains a fraction of it. Mastering a systems language like Rust isn't about skimming more pages; it's about rewiring your mental model until stack frames, heap pointers, `MutexGuard` drop boundaries, and `Pin` invariants snap into focus before you even hit compile.

So **RustForge** was built right inside the terminal where the battle actually happens: no browser tabs, no bloated dependencies, no rainbow distractions. Just monochrome high-contrast focus, ASCII memory maps, real compiler errors to diagnose, and a cognitive engine that refuses to let you move on until you can *predict*, *generate*, and *explain* Rust from scratch.

---

## Why It Works (Neuroscience Architecture)

Every study mode inside RustForge maps directly to peer-reviewed cognitive retention mechanics:

1. **Testing Effect & Prediction-Before-Reveal** — Active retrieval dramatically outperforms rereading ([Roediger & Karpicke, 2006](https://pubmed.ncbi.nlm.nih.gov/16507066/); 61% vs. 40% one-week retention in [retrieval-practice benchmarks](https://yukaichou.com/gamification-analysis/retrieval-practice-testing-effect-roediger-karpicke-learning/)). Every RustForge drill forces you to commit to a prediction before revealing the compiler's behavior, triggering hypercorrection when you miss.
2. **FSRS DSR Spaced Repetition** — Schedules every card using Difficulty (1–10), Stability (days until recall decays to 90%), and Retrievability (`R(t) = (1 + t / (9 * S))^-1`) modeled after the [Free Spaced Repetition Scheduler](https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm) ([FSRS repo](https://github.com/open-spaced-repetition/free-spaced-repetition-scheduler)).
3. **Desirable Difficulties & Interleaving** — Mixing Ownership, Lifetimes, Smart Pointers, Concurrency, and Async drills across chapters forces your brain to *discriminate* which rule applies rather than running on autopilot ([Bjork & Bjork](https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-introducing-desirable-difficulties-into-practice-and-instruction-bjork-and-bjork.pdf); [Desirable difficulty overview](https://en.wikipedia.org/wiki/Desirable_difficulty)).
4. **Generation Effect (Cloze Syntax Drills)** — Producing exact Rust syntax (`&mut`, `'a`, `Box`, `Arc`, `dyn`, `&raw`, `?`, `else`) builds stronger retrieval pathways than passive recognition ([Slamecka & Graf, 1978 / Bertsch et al., 2007](https://www.structural-learning.com/post/generation-effect-active-learning)).
5. **Feynman Self-Explanation** — Explaining mechanisms (like `MutexGuard` drop timing or `Pin`) in plain English exposes hidden illusions of competence ([Chi et al., 1994](https://num8ers.com/guides/top-20-study-techniques-backed-by-science/)).
6. **Dual-Coding Memory Diagrams** — Every chapter pairs plain-English mental models with compact ASCII stack/heap/ownership diagrams.

---

## Quick Start

Requires **Python 3.10+** (standard library only, zero `pip` dependencies). Optional: install `rustc` via [rustup.rs](https://rustup.rs/) to compile and run the 14 live coding labs locally.

```bash
git clone https://github.com/Duckiscutefr/rustforge.git
cd rustforge

# Run immediately (zero install):
python3 -m rustforge

# Or install the `rustforge` command:
./install.sh
```

---

## Commands

| Command | Purpose |
| :--- | :--- |
| `python3 -m rustforge` | Launch interactive dashboard menu |
| `python3 -m rustforge map` | View mastery radar across all 21 chapters |
| `python3 -m rustforge sprint [-m 20]` | Timed focus sprint (FSRS + Interleave + Clinic + Feynman + Peak-End recap) |
| `python3 -m rustforge learn <1-21>` | Study a chapter (mental model, ASCII diagram, rules, recall, cloze, clinic) |
| `python3 -m rustforge review [-n 10]` | FSRS spaced-repetition due review queue |
| `python3 -m rustforge interleave [-n 8]` | Cross-chapter desirable-difficulty drill mixer |
| `python3 -m rustforge debug [1-21]` | Borrow-checker & `rustc` compiler-error diagnostic clinic |
| `python3 -m rustforge feynman [1-21]` | Feynman self-explanation trainer with rubric & concept coverage |
| `python3 -m rustforge lab [chapter]` | Live `rustc --edition 2024 --test` coding labs (graceful offline mode) |
| `python3 -m rustforge ref [A-G]` | Appendices A–G quick reference (keywords, operators, traits, tools, editions) |
| `python3 -m rustforge settings` | Toggle Bionic Reading, target retention (80–95%), and sprint duration |

Flags:
- `--bionic` — Enable Bionic Reading fixation anchors for prose (code blocks and diagrams stay completely unbolded).
- `--no-color` — Disable ANSI styling (also respects the `NO_COLOR` environment variable).
- `--data-file <path>` — Store progress JSON at a custom path (default: `~/.rustforge/progress.json`).

---

## Full Rust 2024 Curriculum Coverage

- **Ch 01–07 (Foundations)**: `rustup`/`rustc`/`cargo`, Guessing Game, Common Concepts & Overflow, Ownership/Borrowing/Slices, Structs & Methods, Enums/`Option`/`match`/`let...else`, Packages/Crates/Modules.
- **Ch 08–14 (Core Systems)**: `Vec`/`String`/UTF-8/`HashMap` Entry API, `panic!`/`Result`/`?`, Generics/Traits/Lifetimes & Elision, Automated Tests, `minigrep` I/O Architecture, Closures (`FnOnce`/`FnMut`/`Fn`) & Zero-Cost Iterators, Cargo Workspaces (`resolver = "3"`) & Doctests.
- **Ch 15–21 (Advanced & Mastery)**: Smart Pointers (`Box`, `Deref`, `Drop`, `Rc`, `RefCell`, `Weak`), Fearless Concurrency (`thread`, `mpsc`, `Arc`, `Mutex`, `Send`/`Sync`), Async/Await/Futures/`Pin`/`Stream`, OOP Trait Objects (`dyn`) & Typestate, Pattern Matching Mastery, Unsafe Rust (2024 `&raw const`/`unsafe extern`), Miri, Associated Types, DSTs, Macros, and the Multithreaded Web Server (`ThreadPool` & `MutexGuard` drop timing).
- **Appendices A–G**: Keywords & `r#` raw identifiers, Operators & Symbols, Derivable Traits, Dev Tools (`rustfmt`, `rustfix`, `clippy`, `rust-analyzer`, `Miri`), Editions (2015–2024), Translations, and Release Trains.

---

## Running Tests

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT

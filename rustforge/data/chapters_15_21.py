"""Chapters 15 to 21 of The Rust Programming Language (2024 Edition)."""

from __future__ import annotations

from rustforge.data.models import (
    Chapter,
    ClozeDrill,
    CodingLab,
    CompilerClinic,
    FeynmanPrompt,
    RecallCard,
)

CHAPTERS_15_21: list[Chapter] = [
    Chapter(
        number=15,
        title="Smart Pointers: Box, Deref, Drop, Rc, RefCell & Weak",
        summary="Heap indirection, deref coercion, deterministic RAII cleanup, reference counting, interior mutability, and breaking cycles.",
        mental_model=(
            "Smart pointers are structs that own data and implement `Deref` (act like a reference) and `Drop` "
            "(run deterministic cleanup on scope exit). Pick the exact pointer for your ownership graph: "
            "`Box<T>` for single-owner heap indirection (recursive types), `Rc<T>` for single-threaded shared "
            "ownership, `RefCell<T>` to move borrow checking from compile time to runtime (interior mutability), "
            "and `Weak<T>` for non-owning back-links that prevent reference-cycle memory leaks."
        ),
        key_rules=(
            "Recursive enums (like cons lists or trees) need `Box<T>` so `rustc` knows the type's finite stack size.",
            "You cannot call `.drop()` manually (that would cause a double-free); use `std::mem::drop(x)` to drop early.",
            "`Rc::clone(&a)` only increments the reference count (O(1))—it does NOT deep-copy the data.",
            "`RefCell<T>` enforces the aliasing XOR mutability rule at RUNTIME: two simultaneous `.borrow_mut()` calls panic.",
            "Combine `Rc<RefCell<T>>` for single-threaded shared mutable state, and use `Weak<T>` (`.upgrade() -> Option<Rc<T>>`) to break parent-child cycles.",
        ),
        diagram_title="SMART POINTER DECISION MATRIX",
        diagram=(
            "  Single owner, heap/recursive type  ---> Box<T>        (compile-time)\n"
            "  Multiple owners, single thread     ---> Rc<T>         (immutable)\n"
            "  Interior mutability, single thread ---> RefCell<T>    (runtime check)\n"
            "  Shared + mutable, single thread    ---> Rc<RefCell<T>>\n"
            "  Break Rc<T> cycles (parent link)   ---> Weak<T>       (.upgrade())"
        ),
        recall_cards=(
            RecallCard(
                id="ch15_c1",
                chapter=15,
                prompt="What happens at runtime if you hold two `RefCell::borrow_mut()` guards on the same `RefCell` in the same scope?",
                code="let cell = RefCell::new(5);\nlet mut a = cell.borrow_mut();\nlet mut b = cell.borrow_mut();",
                options=(
                    "Compile-time borrow checker error",
                    "The program panics at runtime (`already borrowed: BorrowMutError`)",
                    "The second call waits until `a` drops",
                    "Both mutate `cell` unsafely",
                ),
                answer_index=1,
                explanation="`RefCell<T>` checks Rust's borrowing rules at runtime instead of compile time, panicking if two mutable borrows overlap.",
            ),
            RecallCard(
                id="ch15_c2",
                chapter=15,
                prompt="Why does `Rc<T>` + `RefCell<T>` allow memory leaks even in 100% safe Rust, and how do you break them?",
                code="Node A --Rc--> Node B\nNode B --Rc--> Node A",
                options=(
                    "Safe Rust cannot leak memory",
                    "A cycle keeps strong counts >= 1 forever so `Drop` never runs; break it by making the back-reference a `Weak<T>`",
                    "Use `Box::new` instead of `Rc`",
                    "Call `a.drop()` directly",
                ),
                answer_index=1,
                explanation="Preventing memory leaks is NOT a memory-safety guarantee in Rust (though it's rare). Use `Weak<T>` (via `Rc::downgrade`) for non-owning links so strong counts reach 0.",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch15_cl1",
                chapter=15,
                prompt="Give a recursive `List` enum a known compile-time size:",
                code_template="enum List {\n    Cons(i32, ___<List>),\n    Nil,\n}",
                accepted_answers=("Box",),
                hint="Single-owner heap pointer with fixed stack size.",
                explanation="`Box<List>` stores a fixed-size pointer on the stack while placing the next `List` node on the heap.",
            ),
        ),
        clinic=CompilerClinic(
            id="ch15_err",
            chapter=15,
            error_code="E0072",
            title="Recursive type has infinite size",
            broken_code="enum List {\n    Cons(i32, List),\n    Nil,\n}",
            compiler_output=(
                "error[E0072]: recursive type `List` has infinite size\n"
                " --> src/main.rs:1:1\n"
                "  |\n"
                "1 | enum List {\n"
                "  | ^^^^^^^^^\n"
                "2 |     Cons(i32, List),\n"
                "  |               ---- recursive without indirection\n"
                "help: insert some indirection (e.g., a `Box`, `Rc`, or `&`)"
            ),
            question="Why does `Box<List>` fix E0072?",
            options=(
                "A `Box` is a pointer with a fixed, known size on the stack regardless of how deep the list grows on the heap",
                "`Box` makes `List` implement `Copy`",
                "`Box` limits the list to 64 elements",
                "`Box` disables `Drop`",
            ),
            answer_index=0,
            fix_code="enum List {\n    Cons(i32, Box<List>),\n    Nil,\n}",
            mental_model="Every Rust type on the stack must have a statically known size. Indirection (`Box`, `Rc`, `&`) breaks infinite inline nesting.",
        ),
        feynman=FeynmanPrompt(
            chapter=15,
            question="Explain why `std::mem::drop(x)` works to drop a value early while calling `x.drop()` directly is a compile error.",
            rubric_points=(
                "Rust automatically calls `Drop::drop` at the end of scope.",
                "If you were allowed to call `x.drop()` manually, Rust would STILL call it again at scope exit, causing a double-free.",
                "`std::mem::drop` simply takes ownership of `x` by value and does nothing, so `x` is dropped once when `mem::drop` returns.",
            ),
            key_terms=("double-free", "ownership", "scope", "once", "move"),
            model_answer=(
                "If Rust let you call `x.drop()` directly, the compiler would still insert an automatic destructor "
                "call at the end of the block—causing a double-free. `std::mem::drop(x)` takes `x` by value (moving "
                "ownership into an empty function), so it is dropped cleanly exactly once right then."
            ),
        ),
        lab=CodingLab(
            id="lab_ch15_refcell",
            chapter=15,
            title="Mock Logger with `RefCell<Vec<String>>`",
            objective="Implement `MockLogger::send(&self, msg: &str)` using interior mutability (`RefCell`) so `send` takes `&self` while recording messages.",
            starter_code=(
                "use std::cell::RefCell;\n\n"
                "pub trait Messenger {\n"
                "    fn send(&self, msg: &str);\n"
                "}\n\n"
                "pub struct MockLogger {\n"
                "    pub messages: RefCell<Vec<String>>,\n"
                "}\n\n"
                "impl MockLogger {\n"
                "    pub fn new() -> Self { Self { messages: RefCell::new(Vec::new()) } }\n"
                "}\n\n"
                "impl Messenger for MockLogger {\n"
                "    fn send(&self, msg: &str) {\n"
                "        todo!()\n"
                "    }\n"
                "}\n\n"
                "#[cfg(test)]\n"
                "mod tests {\n"
                "    use super::*;\n"
                "    #[test]\n"
                "    fn records_messages() {\n"
                "        let log = MockLogger::new();\n"
                '        log.send("boot");\n'
                '        log.send("ready");\n'
                "        assert_eq!(log.messages.borrow().len(), 2);\n"
                '        assert_eq!(log.messages.borrow()[1], "ready");\n'
                "    }\n"
                "}\n"
            ),
            solution_code=(
                "impl Messenger for MockLogger {\n"
                "    fn send(&self, msg: &str) {\n"
                "        self.messages.borrow_mut().push(msg.to_string());\n"
                "    }\n"
                "}\n"
            ),
        ),
    ),
    Chapter(
        number=16,
        title="Fearless Concurrency: Threads, Channels, Arc & Mutex",
        summary="OS threads, `move` closures, `mpsc` message passing, `Arc<Mutex<T>>` shared state, and `Send`/`Sync` markers.",
        mental_model=(
            "Rust's ownership and type system catch data races at COMPILE TIME. Message passing (`mpsc::channel`) "
            "transfers ownership of values across threads so the sender can never mutate what it already sent. "
            "Shared state wraps the protected data INSIDE `Mutex<T>` (you literally cannot touch `T` without "
            "locking it!) and shares the mutex across threads via atomic reference counting (`Arc<T>`)."
        ),
        key_rules=(
            "`thread::spawn` requires a `move` closure when capturing local values so the thread owns them.",
            "Call `handle.join().unwrap()` to wait for a spawned thread to finish before `main` exits.",
            "`mpsc` = multiple producer, single consumer: clone `tx` for multiple senders; `rx` closes when all `tx` drop.",
            "`Rc<T>` is NOT `Send` (non-atomic counter); use `Arc<T>` across threads.",
            "`Send` = safe to transfer ownership to another thread; `Sync` = safe to share `&T` across threads (`T: Sync` iff `&T: Send`).",
        ),
        diagram_title="THREAD-SAFE SHARED MUTABLE STATE",
        diagram=(
            "  Thread 1: Arc::clone(&counter) --+\n"
            "                                   +--> [ Atomic RefCount | Mutex<i32> ]\n"
            "  Thread 2: Arc::clone(&counter) --+           |\n"
            "                                       .lock().unwrap() -> MutexGuard\n"
            "                                       (auto-unlocks when guard drops!)"
        ),
        recall_cards=(
            RecallCard(
                id="ch16_c1",
                chapter=16,
                prompt="Why does `rustc` reject sharing an `Rc<Mutex<i32>>` across two `thread::spawn` closures?",
                code="let counter = Rc::new(Mutex::new(0));\nlet c = Rc::clone(&counter);\nthread::spawn(move || { *c.lock().unwrap() += 1; });",
                options=(
                    "`Mutex` cannot be placed inside a pointer",
                    "`Rc<T>` does not implement `Send` because its reference count updates are non-atomic and would race across threads",
                    "`thread::spawn` only accepts `Copy` types",
                    "`Mutex::lock` is async-only",
                ),
                answer_index=1,
                explanation="`Rc<T>` omits atomic instructions for single-threaded speed, so it is `!Send`. Use `Arc<T>` (Atomically Reference Counted) for multithreaded sharing.",
            ),
            RecallCard(
                id="ch16_c2",
                chapter=16,
                prompt="What is the difference between the `Send` and `Sync` marker traits?",
                code="unsafe impl Send for MyType {}\nunsafe impl Sync for MyType {}",
                options=(
                    "They are aliases",
                    "`Send` allows transferring ownership of `T` between threads; `Sync` allows sharing `&T` across threads simultaneously",
                    "`Sync` forces a mutex lock; `Send` uses TCP sockets",
                    "`Send` is for async; `Sync` is for threads",
                ),
                answer_index=1,
                explanation="If `T: Send`, you can move `T` to another thread. If `T: Sync`, multiple threads can safely hold `&T` at the same time (which means `&T: Send`).",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch16_cl1",
                chapter=16,
                prompt="Share a `Mutex<i32>` safely across OS threads:",
                code_template="use std::sync::{___, Mutex};\nlet counter = Arc::new(Mutex::new(0));",
                accepted_answers=("Arc",),
                hint="Thread-safe atomic version of `Rc`.",
                explanation="`Arc<T>` uses atomic operations for its reference count, implementing `Send` and `Sync` when `T` does.",
            ),
        ),
        clinic=CompilerClinic(
            id="ch16_err",
            chapter=16,
            error_code="E0373",
            title="Spawned thread borrows local variable without `move`",
            broken_code=(
                "use std::thread;\n"
                "fn main() {\n"
                "    let v = vec![1, 2, 3];\n"
                '    let h = thread::spawn(|| println!("{v:?}"));\n'
                "    h.join().unwrap();\n"
                "}"
            ),
            compiler_output=(
                "error[E0373]: closure may outlive the current function, but it borrows `v`, which is owned by the current function\n"
                " --> src/main.rs:4:27\n"
                "  |\n"
                '4 |     let h = thread::spawn(|| println!("{v:?}"));\n'
                "  |                           ^^           - `v` is borrowed here\n"
                "help: to force the closure to take ownership of `v`, use the `move` keyword"
            ),
            question="Why won't rustc allow the thread to borrow `v` even though `h.join()` is right below it?",
            options=(
                "`thread::spawn` requires `'static` because the compiler cannot prove in general that `v` won't be dropped before the thread finishes",
                "`Vec` cannot be printed in threads",
                "Closures cannot borrow vectors",
                "`h.join()` drops `v` first",
            ),
            answer_index=0,
            fix_code='let h = thread::spawn(move || println!("{v:?}"));',
            mental_model="Use `move ||` to transfer ownership into `thread::spawn` (or use `std::thread::scope` when you genuinely need scoped borrows).",
        ),
        feynman=FeynmanPrompt(
            chapter=16,
            question="Why can't you accidentally forget to lock a `Mutex` in Rust, and why can't you forget to unlock it?",
            rubric_points=(
                "In Rust, `Mutex<T>` OWNS the data `T` inside it—you have no direct access to `T` without calling `.lock()`.",
                "`.lock()` returns a `MutexGuard` smart pointer implementing `DerefMut` and `Drop`.",
                "When the `MutexGuard` leaves scope, its `Drop` impl unlocks the mutex automatically (RAII).",
            ),
            key_terms=("owns", "lock", "MutexGuard", "Drop", "scope"),
            model_answer=(
                "Rust's `Mutex<T>` wraps the protected value inside the mutex itself, so the type system makes it "
                "impossible to touch `T` without calling `.lock()`. Locking hands back a `MutexGuard` whose `Drop` "
                "implementation automatically releases the lock when the guard goes out of scope."
            ),
        ),
        lab=CodingLab(
            id="lab_ch16_counter",
            chapter=16,
            title="Parallel Counter with `Arc<Mutex<usize>>`",
            objective="Spawn `n` threads that each increment a shared `Arc<Mutex<usize>>` by 1, join all threads, and return the final count.",
            starter_code=(
                "use std::sync::{Arc, Mutex};\n"
                "use std::thread;\n\n"
                "pub fn parallel_count(n: usize) -> usize {\n"
                "    todo!()\n"
                "}\n\n"
                "#[cfg(test)]\n"
                "mod tests {\n"
                "    use super::*;\n"
                "    #[test]\n"
                "    fn counts_across_threads() {\n"
                "        assert_eq!(parallel_count(10), 10);\n"
                "        assert_eq!(parallel_count(0), 0);\n"
                "    }\n"
                "}\n"
            ),
            solution_code=(
                "use std::sync::{Arc, Mutex};\n"
                "use std::thread;\n\n"
                "pub fn parallel_count(n: usize) -> usize {\n"
                "    let counter = Arc::new(Mutex::new(0usize));\n"
                "    let mut handles = Vec::with_capacity(n);\n"
                "    for _ in 0..n {\n"
                "        let c = Arc::clone(&counter);\n"
                "        handles.push(thread::spawn(move || {\n"
                "            *c.lock().unwrap() += 1;\n"
                "        }));\n"
                "    }\n"
                "    for h in handles {\n"
                "        h.join().unwrap();\n"
                "    }\n"
                "    *counter.lock().unwrap()\n"
                "}\n"
            ),
        ),
    ),
    Chapter(
        number=17,
        title="Async/Await, Futures, Pin & Streams",
        summary="Cooperative multitasking, lazy `Future::poll`, `join!`/`select`, `Pin`/`Unpin`, and async `Stream`s.",
        mental_model=(
            "Every `async fn` compiles into a zero-allocation state machine implementing `Future` whose `poll()` "
            "returns `Poll::Pending` or `Poll::Ready(T)`. Futures in Rust are LAZY—calling an `async fn` does "
            "nothing until `.await`ed or driven by an async runtime (like Tokio or the Rust Book's `trpl`). "
            "Because state machines can hold self-references across `.await` points, `Pin` guarantees they never "
            "move in memory once polling starts."
        ),
        key_rules=(
            "Each `.await` point is a suspension boundary where the runtime can yield to other tasks (cooperative multitasking).",
            "Do NOT block an async executor with heavy CPU work or `std::thread::sleep`; use async sleep, `yield_now`, or offload CPU work to a thread pool.",
            "`join!` runs multiple futures concurrently and waits for ALL; `select`/`race` returns as soon as the FIRST finishes.",
            "`Pin<P>` prevents moving `!Unpin` futures in memory so internal self-references across `.await` points stay valid.",
            "`Stream` is the async analogue of `Iterator`: yields a sequence of items over time via `StreamExt::next().await`.",
        ),
        diagram_title="ASYNC FUTURE STATE MACHINE & PIN",
        diagram=(
            "  async fn fetch() { let s = step1().await; step2(&s).await; }\n"
            "                         |\n"
            "       Compiler generates enum FetchFuture:\n"
            "       State0 -> poll() -> Pending (registers waker)\n"
            "       State1 { s, ref_to_s } -> MUST NOT MOVE IN MEMORY -> Pin!\n"
            "       State2 -> poll() -> Ready(result)"
        ),
        recall_cards=(
            RecallCard(
                id="ch17_c1",
                chapter=17,
                prompt="What happens if you call `let fut = download_page(url);` without `.await`ing or spawning `fut`?",
                code="async fn download_page(url: &str) -> String { ... }\nlet fut = download_page(\"https://rust-lang.org\");",
                options=(
                    "The HTTP request starts immediately in the background",
                    "Nothing executes yet: Rust futures are lazy and do zero work until polled",
                    "It blocks the current thread",
                    "It panics at runtime",
                ),
                answer_index=1,
                explanation="Unlike JavaScript Promises (eager), Rust `Future`s are lazy state machines—no code inside the `async` body runs until polled.",
            ),
            RecallCard(
                id="ch17_c2",
                chapter=17,
                prompt="Why does `Future::poll(self: Pin<&mut Self>, cx: &mut Context<'_>)` take `Pin<&mut Self>` instead of `&mut Self`?",
                code="fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>",
                options=(
                    "To allocate the future on the stack",
                    "Async state machines can hold internal pointers to their own fields across `.await` points; `Pin` guarantees the future won't be moved in memory and invalidate those pointers",
                    "To make the future implement `Copy`",
                    "To force single-threaded execution",
                ),
                answer_index=1,
                explanation="If a self-referential future were moved to a new memory address via `mem::swap`, its internal reference would dangle. `Pin` forbids moving `!Unpin` values.",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch17_cl1",
                chapter=17,
                prompt="Suspend the current async function until `fut` resolves:",
                code_template="let body = fetch_html(url).___;",
                accepted_answers=("await",),
                hint="Postfix keyword in Rust that polls a Future.",
                explanation="Rust uses postfix `.await` so it chains cleanly with `?` (e.g., `fetch(url).await?`).",
            ),
        ),
        clinic=CompilerClinic(
            id="ch17_err",
            chapter=17,
            error_code="E0277",
            title="Forgetting to pin a `!Unpin` future for `join_all` / polling",
            broken_code=(
                "let f1 = async { 1 };\n"
                "let f2 = async { 2 };\n"
                "let futs: Vec<&mut dyn Future<Output = i32>> = vec![&mut f1, &mut f2];"
            ),
            compiler_output=(
                "error[E0277]: `{async block}` cannot be unpinned\n"
                "  = note: consider using `Box::pin(...)` or `std::pin::pin!(...)`"
            ),
            question="How do you store heterogeneous `async` blocks in a `Vec` so they can be polled?",
            options=(
                "Wrap each future in `Pin<Box<dyn Future<Output = i32>>>` using `Box::pin(f)` (or stack-pin with `pin!`)",
                "Derive `Copy` on the async blocks",
                "Convert them to `Rc<T>`",
                "Remove `async`",
            ),
            answer_index=0,
            fix_code="let futs: Vec<Pin<Box<dyn Future<Output = i32>>>> = vec![Box::pin(f1), Box::pin(f2)];",
            mental_model="Each `async` block has a unique anonymous `!Unpin` type. `Box::pin(...)` both erases the concrete type via `dyn Future` and pins it on the heap.",
        ),
        feynman=FeynmanPrompt(
            chapter=17,
            question="When should you choose OS threads vs. `async`/`.await` in Rust?",
            rubric_points=(
                "Async excels at high-concurrency I/O-bound workloads (thousands of sockets/timers) with tiny per-task memory overhead.",
                "OS threads excel at CPU-bound parallel computation across multiple cores.",
                "You can combine them: async tasks for I/O + thread pools for heavy CPU work, connected via channels.",
            ),
            key_terms=("I/O", "CPU", "threads", "async", "memory"),
            model_answer=(
                "Use `async`/`.await` for I/O-bound workloads with many concurrent tasks (network servers, streams) "
                "because tasks are tiny and switch cooperatively without OS thread overhead. Use OS threads for "
                "CPU-bound parallelism, or combine both with channels."
            ),
        ),
    ),
    Chapter(
        number=18,
        title="Object-Oriented Features & Typestate",
        summary="Encapsulation, trait objects (`Box<dyn Trait>`), static vs. dynamic dispatch, `dyn` compatibility, and typestate.",
        mental_model=(
            "Rust achieves polymorphism without class inheritance. Generics (`T: Draw`) use static dispatch "
            "(monomorphized, fastest, homogeneous collections). Trait objects (`Box<dyn Draw>`) use dynamic "
            "dispatch via a vtable pointer so one `Vec<Box<dyn Draw>>` can hold mixed types. Even better, "
            "Rust's typestate pattern encodes state transitions (`DraftPost -> PendingReviewPost -> Post`) as "
            "distinct types so invalid operations fail at COMPILE TIME."
        ),
        key_rules=(
            "A `Vec<Box<dyn Draw>>` holds heterogeneous types implementing `Draw`; `Vec<T>` holds only one concrete `T`.",
            "Dynamic dispatch (`dyn Trait`) incurs a small vtable indirection and prevents inlining across the call.",
            "`dyn` compatibility (object safety): a trait cannot be used as `dyn Trait` if its methods return `Self` or have generic type parameters.",
            "Typestate replaces runtime `Option`/state checks with compile-time type transitions (`draft.request_review() -> PendingReview`).",
        ),
        diagram_title="STATIC VS. DYNAMIC DISPATCH",
        diagram=(
            "  STATIC:  fn render<T: Draw>(x: &T)   --> specialized per T (inline!)\n"
            "  DYNAMIC: fn render(x: &dyn Draw)     --> fat ptr (data_ptr, vtable_ptr)\n"
            "                                           looks up draw() at runtime\n"
            "\n"
            "  TYPESTATE: DraftPost --request_review(self)--> PendingReviewPost\n"
            "             PendingReviewPost --approve(self)--> PublishedPost"
        ),
        recall_cards=(
            RecallCard(
                id="ch18_c1",
                chapter=18,
                prompt="Why can't you create a `Box<dyn Clone>` trait object?",
                code="let items: Vec<Box<dyn Clone>> = vec![];",
                options=(
                    "`Clone` is private",
                    "`Clone::clone(&self) -> Self` returns `Self` (whose size is unknown behind `dyn`), making `Clone` not `dyn`-compatible",
                    "`Box` does not work with traits",
                    "`Vec` only accepts `Copy` types",
                ),
                answer_index=1,
                explanation="Methods returning `Self` by value require knowing the concrete type's size at the call site, which a `dyn` trait object erases.",
            ),
            RecallCard(
                id="ch18_c2",
                chapter=18,
                prompt="What is the big advantage of Rust's typestate pattern over the classic OOP State pattern?",
                code="let post = DraftPost::new();\nlet post = post.request_review();\nlet post = post.approve();",
                options=(
                    "It uses more heap allocations",
                    "Invalid state operations (like reading content of a `DraftPost`) become COMPILE-TIME errors instead of runtime bugs",
                    "It allows cyclic inheritance",
                    "It requires `unsafe`",
                ),
                answer_index=1,
                explanation="Because `DraftPost` literally does not define `.content()`, trying to publish or read a draft is caught by `rustc` before the program ever runs.",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch18_cl1",
                chapter=18,
                prompt="Declare a vector that can hold any heterogeneous type implementing the `Draw` trait:",
                code_template="pub struct Screen {\n    pub components: Vec<Box<___ Draw>>,\n}",
                accepted_answers=("dyn",),
                hint="Keyword prefix for dynamically dispatched trait objects.",
                explanation="`Box<dyn Draw>` is a heap-allocated trait object enabling heterogeneous collections.",
            ),
        ),
        clinic=CompilerClinic(
            id="ch18_err",
            chapter=18,
            error_code="E0038",
            title="Trait is not `dyn` compatible (object-safe)",
            broken_code=(
                "trait Builder {\n"
                "    fn clone_me(&self) -> Self;\n"
                "}\n"
                "fn run(b: &dyn Builder) { let _ = b.clone_me(); }"
            ),
            compiler_output=(
                "error[E0038]: the trait `Builder` is not dyn compatible\n"
                "  = note: method `clone_me` references the `Self` type in its return type"
            ),
            question="How do you make `Builder` `dyn`-compatible?",
            options=(
                "Return `Box<dyn Builder>` instead of bare `Self` (or bound the method with `where Self: Sized`)",
                "Add `#[derive(Copy)]` to `Builder`",
                "Replace `&dyn` with `&mut`",
                "Mark `Builder` as `unsafe`",
            ),
            answer_index=0,
            fix_code="trait Builder {\n    fn clone_boxed(&self) -> Box<dyn Builder>;\n}",
            mental_model="Behind `dyn Trait`, the caller doesn't know `Self`'s concrete stack size. Return a `Box<dyn Trait>` instead.",
        ),
        feynman=FeynmanPrompt(
            chapter=18,
            question="Compare `struct Screen<T: Draw> { components: Vec<T> }` with `struct Screen { components: Vec<Box<dyn Draw>> }`.",
            rubric_points=(
                "Generic `Vec<T>` is homogeneous (all elements must be the same concrete type) and uses fast static dispatch.",
                "`Vec<Box<dyn Draw>>` is heterogeneous (can mix Buttons, SelectBoxes, etc.) and uses runtime vtable dynamic dispatch.",
                "Pick generics for performance/uniform types and `dyn Trait` when you need mixed types at runtime.",
            ),
            key_terms=("homogeneous", "heterogeneous", "static", "dynamic", "vtable"),
            model_answer=(
                "`Vec<T>` can only hold one concrete type at a time (e.g., all `Button`s) and compiles to zero-overhead "
                "static dispatch. `Vec<Box<dyn Draw>>` can mix any types implementing `Draw` in the same list at the "
                "small cost of heap boxing and vtable dynamic dispatch."
            ),
        ),
        lab=CodingLab(
            id="lab_ch18_typestate",
            chapter=18,
            title="Compile-Time Typestate Workflow",
            objective="Implement `Draft -> Pending -> Published` where only `Published` exposes `.content() -> &str`.",
            starter_code=(
                "pub struct Draft { text: String }\n"
                "pub struct Pending { text: String }\n"
                "pub struct Published { text: String }\n\n"
                "impl Draft {\n"
                "    pub fn new(text: &str) -> Self { Self { text: text.to_string() } }\n"
                "    pub fn request_review(self) -> Pending { todo!() }\n"
                "}\n"
                "impl Pending {\n"
                "    pub fn approve(self) -> Published { todo!() }\n"
                "}\n"
                "impl Published {\n"
                "    pub fn content(&self) -> &str { todo!() }\n"
                "}\n\n"
                "#[cfg(test)]\n"
                "mod tests {\n"
                "    use super::*;\n"
                "    #[test]\n"
                "    fn transitions_state() {\n"
                '        let post = Draft::new("Rust 2024").request_review().approve();\n'
                '        assert_eq!(post.content(), "Rust 2024");\n'
                "    }\n"
                "}\n"
            ),
            solution_code=(
                "impl Draft {\n"
                "    pub fn new(text: &str) -> Self { Self { text: text.to_string() } }\n"
                "    pub fn request_review(self) -> Pending { Pending { text: self.text } }\n"
                "}\n"
                "impl Pending {\n"
                "    pub fn approve(self) -> Published { Published { text: self.text } }\n"
                "}\n"
                "impl Published {\n"
                "    pub fn content(&self) -> &str { &self.text }\n"
                "}\n"
            ),
        ),
    ),
    Chapter(
        number=19,
        title="Patterns and Matching Mastery",
        summary="Refutable vs. irrefutable patterns, destructuring, `_` vs `_x` move semantics, `..`, match guards, and `@` bindings.",
        mental_model=(
            "Patterns appear everywhere in Rust—not just `match`, but `let`, `for`, function parameters, `if let`, "
            "`while let`, and `let...else`. Irrefutable patterns (like `let (x, y) = pair;`) can never fail; "
            "refutable patterns (like `Some(x)`) can fail and belong in `if let`, `while let`, `let...else`, or `match`."
        ),
        key_rules=(
            "`_` ignores a value WITHOUT binding or moving it; `_x` DOES bind (and moves non-Copy values!).",
            "`..` ignores remaining fields/elements (e.g., `Point { x, .. }` or `(first, .., last)`).",
            "Match guards (`Some(x) if x % 2 == 0 => ...`) add extra conditions; note `4 | 5 | 6 if y` applies `if y` to ALL three alternatives.",
            "`@` bindings (`id @ 3..=7`) test a value against a pattern AND capture it into a variable simultaneously.",
        ),
        diagram_title="`_` VS. `_x` OWNERSHIP TRAP",
        diagram=(
            "  let s = Some(String::from(\"hi\"));\n"
            "  if let Some(_s) = s { ... }  // MOVES String into `_s` -> `s` invalid!\n"
            "  if let Some(_)  = s { ... }  // Does NOT bind/move    -> `s` still valid!"
        ),
        recall_cards=(
            RecallCard(
                id="ch19_c1",
                chapter=19,
                prompt="Will `println!(\"{s:?}\")` compile after `if let Some(_s) = s {}` where `s = Some(String::from(\"hi\"))`?",
                code='let s = Some(String::from("hi"));\nif let Some(_s) = s {}\nprintln!("{s:?}");',
                options=(
                    "Yes, leading underscore prevents moving",
                    "No (E0382): `_s` still binds and moves the `String` out of `s`; use `_` to avoid moving",
                    "Yes, `if let` always borrows",
                    "Only in Edition 2024",
                ),
                answer_index=1,
                explanation="`_s` is a normal variable binding that silences unused-variable warnings—it still moves! Only bare `_` avoids binding/moving.",
            ),
            RecallCard(
                id="ch19_c2",
                chapter=19,
                prompt="What does `Message::Hello { id: id_var @ 3..=7 }` do?",
                code="match msg {\n    Message::Hello { id: id_var @ 3..=7 } => println!(\"in range: {id_var}\"),\n    _ => {}\n}",
                options=(
                    "Checks that `id` is between 3 and 7 inclusive AND binds its value to `id_var`",
                    "Mutates `id` to 3",
                    "Matches any `id` outside 3..=7",
                    "Creates a reference to a range",
                ),
                answer_index=0,
                explanation="The `@` operator lets you simultaneously test a value against a pattern and capture it in a variable.",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch19_cl1",
                chapter=19,
                prompt="Destructure only the `x` field of `Point3D { x, y, z }` while ignoring the rest:",
                code_template="let Point3D { x, ___ } = origin;",
                accepted_answers=("..",),
                hint="Two dots ignoring remaining struct fields.",
                explanation="`..` ignores all remaining fields cleanly without naming `y` or `z`.",
            ),
        ),
        clinic=CompilerClinic(
            id="ch19_err",
            chapter=19,
            error_code="E0005",
            title="Refutable pattern in local `let` binding",
            broken_code="let opt = Some(5);\nlet Some(x) = opt;",
            compiler_output=(
                "error[E0005]: refutable pattern in local binding\n"
                " --> src/main.rs:2:5\n"
                "  |\n"
                "2 | let Some(x) = opt;\n"
                "  |     ^^^^^^^ pattern `None` not covered\n"
                "help: you might want to use `let else` to handle the variant that isn't matched"
            ),
            question="Why does `let Some(x) = opt;` fail even though line 1 assigned `Some(5)`?",
            options=(
                "`let` requires an irrefutable pattern based on the static type `Option<i32>`, which includes `None`",
                "`Option` cannot be destructured",
                "`x` must be `mut`",
                "`Some(5)` is a tuple",
            ),
            answer_index=0,
            fix_code="let Some(x) = opt else { return; };",
            mental_model="Use `if let`, `let...else`, or `match` whenever a pattern can fail to match the static type.",
        ),
        feynman=FeynmanPrompt(
            chapter=19,
            question="Explain the difference between refutable and irrefutable patterns, and give one place each is required.",
            rubric_points=(
                "Irrefutable patterns match every possible value of the type (e.g., `let x = 5;`, function params, `for`).",
                "Refutable patterns can fail to match (e.g., `Some(x)` on `Option<T>`).",
                "Refutable patterns belong in `if let`, `while let`, `let...else`, and `match` arms.",
            ),
            key_terms=("irrefutable", "refutable", "let", "if let", "match"),
            model_answer=(
                "An irrefutable pattern matches every possible value of its type (required in `let`, function "
                "parameters, and `for` loops). A refutable pattern can fail on some values (like `Some(x)` when "
                "given `None`) and is used in `if let`, `while let`, `let...else`, or `match`."
            ),
        ),
        lab=CodingLab(
            id="lab_ch19_pattern",
            chapter=19,
            title="Pattern Guards & `@` Range Binding",
            objective="Classify HTTP status codes using `@` bindings and match guards: 200..=299 -> Ok(code), 404 -> NotFound, 500..=599 -> ServerErr(code), else Other.",
            starter_code=(
                "#[derive(Debug, PartialEq)]\n"
                "pub enum Status { Ok(u16), NotFound, ServerErr(u16), Other }\n\n"
                "pub fn classify(code: u16) -> Status {\n"
                "    todo!()\n"
                "}\n\n"
                "#[cfg(test)]\n"
                "mod tests {\n"
                "    use super::*;\n"
                "    #[test]\n"
                "    fn classifies_codes() {\n"
                "        assert_eq!(classify(200), Status::Ok(200));\n"
                "        assert_eq!(classify(404), Status::NotFound);\n"
                "        assert_eq!(classify(503), Status::ServerErr(503));\n"
                "        assert_eq!(classify(302), Status::Other);\n"
                "    }\n"
                "}\n"
            ),
            solution_code=(
                "pub fn classify(code: u16) -> Status {\n"
                "    match code {\n"
                "        c @ 200..=299 => Status::Ok(c),\n"
                "        404 => Status::NotFound,\n"
                "        c @ 500..=599 => Status::ServerErr(c),\n"
                "        _ => Status::Other,\n"
                "    }\n"
                "}\n"
            ),
        ),
    ),
    Chapter(
        number=20,
        title="Advanced Features: Unsafe, Traits, Types & Macros",
        summary="5 unsafe superpowers (Rust 2024 `&raw const`/`unsafe extern`), Miri, associated types, `!`, DSTs/`?Sized`, and macros.",
        mental_model=(
            "`unsafe` does NOT turn off the borrow checker! It unlocks exactly 5 extra superpowers where YOU "
            "uphold memory-safety invariants and wrap them in a safe abstraction. Rust 2024 tightens unsafe "
            "ergonomics (`&raw const`/`&raw mut`, `unsafe extern \"C\"`, `#[unsafe(no_mangle)]`). Beyond unsafe, "
            "associated types, supertraits, newtypes, `!` (never type), DSTs (`?Sized`), and macros let you "
            "build expressive zero-cost DSLs and libraries."
        ),
        key_rules=(
            "The 5 unsafe superpowers: (1) dereference a raw pointer, (2) call an unsafe fn/method, (3) access/modify a mutable static, (4) implement an unsafe trait, (5) access fields of a `union`.",
            "Creating a raw pointer (`&raw const x`, `&raw mut x`) is SAFE; only DEREFERENCING it requires `unsafe`.",
            "Use `Miri` (`cargo +nightly miri test`) to detect undefined behavior in `unsafe` code.",
            "Associated types (`type Item;` in `Iterator`) allow ONE impl per type; generic trait params (`Add<Rhs>`) allow MULTIPLE impls per type.",
            "Dynamically Sized Types (`str`, `[T]`, `dyn Trait`) must live behind a pointer (`&`, `Box`, `Rc`); generic params implicitly have `T: Sized` unless relaxed with `T: ?Sized`.",
            "Declarative macros (`macro_rules!`) match AST patterns; procedural macros (`derive`, attribute, function-like) transform `TokenStream`s in a `proc-macro` crate.",
        ),
        diagram_title="THE 5 UNSAFE SUPERPOWERS (RUST 2024)",
        diagram=(
            "  unsafe { ... }  <-- Borrow checker STILL RUNS! Only unlocks:\n"
            "   1. Dereference raw pointers (*const T / *mut T)\n"
            "   2. Call unsafe fn / unsafe extern \"C\" FFI\n"
            "   3. Access/modify `static mut`\n"
            "   4. Implement `unsafe trait` (e.g., Send / Sync)\n"
            "   5. Read fields of a C-style `union`"
        ),
        recall_cards=(
            RecallCard(
                id="ch20_c1",
                chapter=20,
                prompt="Does wrapping code in an `unsafe { ... }` block disable Rust's borrow checker for regular `&T` / `&mut T` references?",
                code="unsafe {\n    let mut x = 5;\n    let r1 = &mut x;\n    let r2 = &mut x;\n}",
                options=(
                    "Yes, `unsafe` disables all compiler checks",
                    "No: the borrow checker and type checker still run fully inside `unsafe`; it only unlocks the 5 specific superpowers",
                    "Only in release mode",
                    "Only for stack variables",
                ),
                answer_index=1,
                explanation="`unsafe` is surgical, not a blanket escape hatch—the borrow checker still enforces aliasing rules on normal references inside `unsafe`.",
            ),
            RecallCard(
                id="ch20_c2",
                chapter=20,
                prompt="Why does `Iterator` use an associated type (`type Item;`) instead of a generic parameter (`trait Iterator<T>`)?",
                code="pub trait Iterator {\n    type Item;\n    fn next(&mut self) -> Option<Self::Item>;\n}",
                options=(
                    "Generics cannot be used in traits",
                    "So each type has ONE unambiguous `Iterator` impl and callers don't have to annotate `T` every time they call `.next()`",
                    "Associated types are faster at runtime",
                    "Only `std` can use associated types",
                ),
                answer_index=1,
                explanation="With `type Item;`, a type can implement `Iterator` only once—eliminating type-inference ambiguity at every `.next()` call.",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch20_cl1",
                chapter=20,
                prompt="Create an immutable raw pointer to `num` using Rust 2024 syntax (safe without creating an intermediate reference):",
                code_template="let mut num = 5;\nlet r1 = ___ const num;",
                accepted_answers=("&raw",),
                hint="Rust 2024 raw-borrow operator.",
                explanation="`&raw const num` and `&raw mut num` create raw pointers directly without triggering intermediate reference aliasing UB.",
            ),
        ),
        clinic=CompilerClinic(
            id="ch20_err",
            chapter=20,
            error_code="E0133",
            title="Dereferencing a raw pointer outside `unsafe`",
            broken_code=(
                "let num = 42;\n"
                "let ptr = &raw const num;\n"
                'println!("{}", *ptr);'
            ),
            compiler_output=(
                "error[E0133]: dereference of raw pointer is unsafe and requires unsafe function or block\n"
                " --> src/main.rs:3:16\n"
                "  |\n"
                '3 | println!("{}", *ptr);\n'
                "  |                ^^^^ dereference of raw pointer"
            ),
            question="Which line actually needs `unsafe`?",
            options=(
                "Only `*ptr` (dereferencing); creating `ptr` with `&raw const num` is completely safe",
                "Both creating `ptr` and dereferencing `*ptr`",
                "Only `let ptr = ...`",
                "Neither—just mark `num` as `mut`",
            ),
            answer_index=0,
            fix_code='let num = 42;\nlet ptr = &raw const num;\nunsafe { println!("{}", *ptr); }',
            mental_model="Keep `unsafe` blocks as tiny as possible and document the exact `// SAFETY:` invariant proving the pointer is valid and aligned.",
        ),
        feynman=FeynmanPrompt(
            chapter=20,
            question="Why does Rust's standard library use `unsafe` inside `slice::split_at_mut`, yet expose it as a 100% safe function?",
            rubric_points=(
                "The borrow checker sees two `&mut` borrows from the same slice and cannot prove the two halves don't overlap.",
                "Inside `split_at_mut`, a tiny `unsafe` block uses `from_raw_parts_mut` after asserting `mid <= len`.",
                "Because the function guarantees the two returned slices are disjoint, its public API is completely sound and safe.",
            ),
            key_terms=("disjoint", "overlap", "safe abstraction", "bounds", "raw"),
            model_answer=(
                "The borrow checker treats a slice as one unit and can't verify that `0..mid` and `mid..len` don't "
                "overlap. `split_at_mut` checks `assert!(mid <= len)`, uses a tiny `unsafe` block to construct two "
                "disjoint mutable slices via raw pointers, and exposes a sound, safe API."
            ),
        ),
        lab=CodingLab(
            id="lab_ch20_macro",
            chapter=20,
            title="Declarative Macro & Newtype Wrapper",
            objective="Write a `macro_rules! string_vec` that constructs a `Vec<String>` from comma-separated `&str` literals.",
            starter_code=(
                "#[macro_export]\n"
                "macro_rules! string_vec {\n"
                "    // TODO: match $( $x:expr ),* $(,)? and build Vec<String>\n"
                "    () => { Vec::<String>::new() };\n"
                "}\n\n"
                "#[cfg(test)]\n"
                "mod tests {\n"
                "    #[test]\n"
                "    fn builds_string_vec() {\n"
                '        let v = string_vec!["rust", "2024",];\n'
                '        assert_eq!(v, vec![String::from("rust"), String::from("2024")]);\n'
                "        let empty: Vec<String> = string_vec![];\n"
                "        assert!(empty.is_empty());\n"
                "    }\n"
                "}\n"
            ),
            solution_code=(
                "#[macro_export]\n"
                "macro_rules! string_vec {\n"
                "    ( $( $x:expr ),* $(,)? ) => {\n"
                "        {\n"
                "            let mut temp = Vec::new();\n"
                "            $(\n"
                "                temp.push(String::from($x));\n"
                "            )*\n"
                "            temp\n"
                "        }\n"
                "    };\n"
                "}\n"
            ),
        ),
    ),
    Chapter(
        number=21,
        title="Final Project: Multithreaded Web Server",
        summary="`TcpListener`, HTTP parsing, `ThreadPool` + `Worker`, `Arc<Mutex<mpsc::Receiver<Job>>>`, `MutexGuard` drop timing, and graceful `Drop`.",
        mental_model=(
            "Chapter 21 fuses the entire book into one systems architecture: `TcpListener` accepts sockets, a "
            "fixed-size `ThreadPool` bounds concurrency against DoS exhaustion, `Worker` threads share a single "
            "`mpsc::Receiver<Job>` wrapped in `Arc<Mutex<...>>`, and `Drop for ThreadPool` drops the `Option<Sender>` "
            "first so every worker's `recv()` returns `Err`, exits cleanly, and gets `.join()`ed."
        ),
        key_rules=(
            "`type Job = Box<dyn FnOnce() + Send + 'static>;` lets any one-shot closure be sent to a worker thread.",
            "CRITICAL LOCK BUG: `let message = receiver.lock().unwrap().recv();` drops the `MutexGuard` right at `;` BEFORE running `job()`. In contrast, `while let Ok(job) = receiver.lock().unwrap().recv() { job(); }` holds the lock FOR THE ENTIRE BODY of `job()`, destroying parallelism!",
            "Wrap `sender` in `Option<mpsc::Sender<Job>>` and call `drop(self.sender.take())` in `Drop` to close the channel before joining worker threads.",
            "Use `self.workers.drain(..)` (or `Option<JoinHandle<()>>` + `.take()`) in `Drop` because `join(self)` requires owning the `JoinHandle`, whereas `drop(&mut self)` only gives `&mut self`.",
        ),
        diagram_title="THREADPOOL ARCHITECTURE & GRACEFUL SHUTDOWN",
        diagram=(
            "  TcpListener --> ThreadPool::execute(Job)\n"
            "                      |\n"
            "                 Option<Sender<Job>>  (dropped FIRST in Drop!)\n"
            "                      |\n"
            "               Arc<Mutex<Receiver<Job>>>\n"
            "                /        |         \\\n"
            "           Worker 0   Worker 1   Worker 2  (each calls join() on Drop)"
        ),
        recall_cards=(
            RecallCard(
                id="ch21_c1",
                chapter=21,
                prompt="Why does `while let Ok(job) = receiver.lock().unwrap().recv() { job(); }` serialize all workers instead of running them in parallel?",
                code="while let Ok(job) = receiver.lock().unwrap().recv() {\n    job(); // <-- BUG!\n}",
                options=(
                    "`recv()` blocks all threads permanently",
                    "Temporary values (`MutexGuard`) in `while let` stay alive for the ENTIRE loop body, holding the mutex locked while `job()` runs",
                    "`Job` is not `Send`",
                    "`Arc` allows only one thread at a time",
                ),
                answer_index=1,
                explanation="With `let message = receiver.lock().unwrap().recv();`, the temporary `MutexGuard` drops immediately at the semicolon BEFORE `job()` executes, freeing other workers to grab the next job.",
            ),
            RecallCard(
                id="ch21_c2",
                chapter=21,
                prompt="In `Drop for ThreadPool`, why MUST you drop `self.sender` BEFORE calling `worker.thread.join()`?",
                code="drop(self.sender.take());\nfor worker in self.workers.drain(..) { worker.thread.join().unwrap(); }",
                options=(
                    "To free RAM faster",
                    "Deadlock prevention: workers loop on `recv()` until the channel closes (all senders dropped); joining before dropping `sender` waits forever",
                    "`JoinHandle::join` refuses to compile otherwise",
                    "`mpsc` requires dropping senders in alphabetical order",
                ),
                answer_index=1,
                explanation="Dropping `sender` closes the channel so each worker's `recv()` returns `Err` and breaks out of its loop, allowing `.join()` to finish cleanly.",
            ),
        ),
        cloze_drills=(
            ClozeDrill(
                id="ch21_cl1",
                chapter=21,
                prompt="Define the `Job` type alias for one-shot closures sent across threads:",
                code_template="type Job = Box<dyn ___() + Send + 'static>;",
                accepted_answers=("FnOnce",),
                hint="Closure trait for a task executed exactly once.",
                explanation="`Box<dyn FnOnce() + Send + 'static>` accepts any owned closure that runs once on a worker thread.",
            ),
        ),
        clinic=CompilerClinic(
            id="ch21_err",
            chapter=21,
            error_code="E0507",
            title="Cannot move `JoinHandle` out of `&mut self` in `Drop`",
            broken_code=(
                "impl Drop for ThreadPool {\n"
                "    fn drop(&mut self) {\n"
                "        for worker in &mut self.workers {\n"
                "            worker.thread.join().unwrap();\n"
                "        }\n"
                "    }\n"
                "}"
            ),
            compiler_output=(
                "error[E0507]: cannot move out of `worker.thread` which is behind a mutable reference\n"
                " --> src/lib.rs:4:13\n"
                "  |\n"
                "4 | worker.thread.join().unwrap();\n"
                "  | ^^^^^^^^^^^^^ move occurs because `worker.thread` has type `JoinHandle<()>`, which does not implement `Copy`"
            ),
            question="How do you legally take ownership of each `JoinHandle` inside `drop(&mut self)`?",
            options=(
                "Use `self.workers.drain(..)` (or store `Option<JoinHandle<()>>` and call `.take()`)",
                "Derive `Copy` on `JoinHandle`",
                "Clone `worker.thread`",
                "Change `fn drop(self)` to take `self` by value",
            ),
            answer_index=0,
            fix_code="for worker in self.workers.drain(..) {\n    worker.thread.join().unwrap();\n}",
            mental_model="`Drop::drop` always receives `&mut self`. Use `Vec::drain(..)` or `Option::take()` to move owned resources out cleanly.",
        ),
        feynman=FeynmanPrompt(
            chapter=21,
            question="Walk through the exact lifetime of the `MutexGuard` in `let msg = rx.lock().unwrap().recv();` vs. `while let Ok(job) = rx.lock().unwrap().recv() { job(); }`.",
            rubric_points=(
                "In a `let` statement, temporaries on the right-hand side drop at the semicolon, so the lock is released BEFORE `job()` runs.",
                "In `while let` (and `if let`/`match`), temporaries in the scrutinee stay alive until the end of the associated block.",
                "Holding the lock during `job()` forces all other workers to wait, turning a multithreaded pool into single-threaded execution.",
            ),
            key_terms=("MutexGuard", "temporary", "semicolon", "while let", "parallel"),
            model_answer=(
                "In `let msg = rx.lock().unwrap().recv();`, the temporary `MutexGuard` drops right at the `;` before "
                "`job()` runs, so other workers can immediately acquire the lock. In `while let`, temporaries live "
                "until the end of the loop body—keeping the mutex locked for the entire duration of `job()`."
            ),
        ),
        lab=CodingLab(
            id="lab_ch21_pool",
            chapter=21,
            title="Mini Graceful ThreadPool",
            objective="Build a minimal `ThreadPool` with `new(size)`, `execute(f)`, and graceful `Drop` that joins all workers.",
            starter_code=(
                "use std::sync::{mpsc, Arc, Mutex};\n"
                "use std::thread;\n\n"
                "type Job = Box<dyn FnOnce() + Send + 'static>;\n\n"
                "pub struct ThreadPool {\n"
                "    workers: Vec<thread::JoinHandle<()>>,\n"
                "    sender: Option<mpsc::Sender<Job>>,\n"
                "}\n\n"
                "impl ThreadPool {\n"
                "    pub fn new(size: usize) -> Self { todo!() }\n"
                "    pub fn execute<F: FnOnce() + Send + 'static>(&self, f: F) { todo!() }\n"
                "}\n\n"
                "impl Drop for ThreadPool {\n"
                "    fn drop(&mut self) { todo!() }\n"
                "}\n\n"
                "#[cfg(test)]\n"
                "mod tests {\n"
                "    use super::*;\n"
                "    use std::sync::atomic::{AtomicUsize, Ordering};\n"
                "    #[test]\n"
                "    fn executes_all_jobs_before_drop() {\n"
                "        let done = Arc::new(AtomicUsize::new(0));\n"
                "        {\n"
                "            let pool = ThreadPool::new(4);\n"
                "            for _ in 0..8 {\n"
                "                let d = Arc::clone(&done);\n"
                "                pool.execute(move || { d.fetch_add(1, Ordering::SeqCst); });\n"
                "            }\n"
                "        }\n"
                "        assert_eq!(done.load(Ordering::SeqCst), 8);\n"
                "    }\n"
                "}\n"
            ),
            solution_code=(
                "impl ThreadPool {\n"
                "    pub fn new(size: usize) -> Self {\n"
                "        assert!(size > 0);\n"
                "        let (sender, receiver) = mpsc::channel::<Job>();\n"
                "        let receiver = Arc::new(Mutex::new(receiver));\n"
                "        let mut workers = Vec::with_capacity(size);\n"
                "        for _ in 0..size {\n"
                "            let rx = Arc::clone(&receiver);\n"
                "            workers.push(thread::spawn(move || loop {\n"
                "                let msg = rx.lock().unwrap().recv();\n"
                "                match msg {\n"
                "                    Ok(job) => job(),\n"
                "                    Err(_) => break,\n"
                "                }\n"
                "            }));\n"
                "        }\n"
                "        Self { workers, sender: Some(sender) }\n"
                "    }\n"
                "    pub fn execute<F: FnOnce() + Send + 'static>(&self, f: F) {\n"
                "        if let Some(tx) = &self.sender {\n"
                "            tx.send(Box::new(f)).unwrap();\n"
                "        }\n"
                "    }\n"
                "}\n\n"
                "impl Drop for ThreadPool {\n"
                "    fn drop(&mut self) {\n"
                "        drop(self.sender.take());\n"
                "        for handle in self.workers.drain(..) {\n"
                "            handle.join().unwrap();\n"
                "        }\n"
                "    }\n"
                "}\n"
            ),
        ),
    ),
]

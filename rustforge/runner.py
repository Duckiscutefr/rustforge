"""Live rustc coding lab runner with graceful offline fallback."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LabRunResult:
    available: bool
    compiled: bool
    passed: bool
    stdout: str
    stderr: str
    edition_used: str = "2024"


def rustc_version() -> str | None:
    """Return `rustc --version` output if rustc is installed, else None."""
    if not shutil.which("rustc"):
        return None
    try:
        proc = subprocess.run(
            ["rustc", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except OSError:
        return None
    return None


def compile_and_test_rust(source_code: str, edition: str = "2024", timeout_sec: int = 15) -> LabRunResult:
    """Compile and execute a Rust snippet with `--test` in a temporary directory."""
    if not shutil.which("rustc"):
        return LabRunResult(
            available=False,
            compiled=False,
            passed=False,
            stdout="",
            stderr="rustc not found on PATH. Install via https://rustup.rs/ to run live compilation.",
            edition_used=edition,
        )

    with tempfile.TemporaryDirectory(prefix="rustforge_lab_") as tmpdir:
        tmp = Path(tmpdir)
        src = tmp / "lab.rs"
        exe = tmp / "lab_test"
        src.write_text(source_code, encoding="utf-8")

        # Try Edition 2024 first, fall back to 2021 if user has an older toolchain
        editions_to_try = [edition] + (["2021"] if edition == "2024" else [])
        compile_proc = None
        used_edition = edition
        for ed in editions_to_try:
            used_edition = ed
            compile_proc = subprocess.run(
                ["rustc", "--edition", ed, "--test", str(src), "-o", str(exe)],
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                check=False,
            )
            if compile_proc.returncode == 0 or "unsupported edition" not in compile_proc.stderr.lower():
                break

        assert compile_proc is not None
        if compile_proc.returncode != 0:
            return LabRunResult(
                available=True,
                compiled=False,
                passed=False,
                stdout=compile_proc.stdout,
                stderr=compile_proc.stderr,
                edition_used=used_edition,
            )

        try:
            run_proc = subprocess.run(
                [str(exe), "--nocapture"],
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return LabRunResult(
                available=True,
                compiled=True,
                passed=False,
                stdout="",
                stderr=f"Test execution timed out after {timeout_sec}s (check for infinite loops or deadlocks).",
                edition_used=used_edition,
            )

        return LabRunResult(
            available=True,
            compiled=True,
            passed=run_proc.returncode == 0,
            stdout=run_proc.stdout,
            stderr=run_proc.stderr,
            edition_used=used_edition,
        )


def lab_workspace_file(lab_id: str, starter_code: str) -> Path:
    """Create or locate the user's editable Rust lab file under ~/.rustforge/labs/."""
    lab_dir = Path.home() / ".rustforge" / "labs"
    lab_dir.mkdir(parents=True, exist_ok=True)
    path = lab_dir / f"{lab_id}.rs"
    if not path.exists():
        path.write_text(starter_code.strip() + "\n", encoding="utf-8")
    return path

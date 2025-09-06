#!/usr/bin/env python3
"""Environment checker for the buttons project.

Lightweight checks for Python, key modules, and KiCad tooling. Designed to be
safe to run in local dev shells and CI. Exits with 0 on success, nonzero on
major failures.
"""
from __future__ import annotations
import os
import shutil
import subprocess
import sys


def check_python(min_major: int = 3, min_minor: int = 11) -> bool:
    v = sys.version_info
    ok = (v.major, v.minor) >= (min_major, min_minor)
    status = "OK" if ok else f"OLD (needs >= {min_major}.{min_minor})"
    print(f"python: {v.major}.{v.minor}.{v.micro} -> {status}")
    return ok


def check_module(name: str) -> bool:
    try:
        m = __import__(name)
        ver = getattr(m, "__version__", None)
        print(f"module: {name} present (version={ver})")
        return True
    except Exception as exc:
        print(f"module: {name} MISSING ({exc.__class__.__name__})")
        return False


def run_cmd(cmd: list[str]) -> str | None:
    exe = shutil.which(cmd[0])
    if not exe:
        print(f"cmd: {cmd[0]} not found in PATH")
        return None
    try:
        # Use subprocess.run with a short timeout to avoid launching GUI apps
        # that may not exit (macOS KiCad binary can open a GUI and block).
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=6,
        )
        out = proc.stdout or ""
        first = out.splitlines()[0] if out else ""
        print(f"cmd: {' '.join(cmd)} -> {first}")
        if proc.returncode != 0:
            print(f"cmd: {' '.join(cmd)} -> exit {proc.returncode}")
        return out
    except subprocess.TimeoutExpired:
        print(f"cmd: {' '.join(cmd)} -> timed out")
        return None
    except subprocess.CalledProcessError as e:
        print(f"cmd: {' '.join(cmd)} -> error (exit {e.returncode})")
        return None


def git_sha_short() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True
        ).strip()
        print(f"git: HEAD {out}")
        return out
    except Exception:
        print("git: not available or not a git repo")
        return None


def main() -> int:
    """Run checks and return an exit code.

    If the environment variable BUTTONS_IGNORE_PYTHON_CHECK is set the
    Python-version mismatch will be allowed (useful for continuing work on
    systems where upgrading Python is not possible right now).
    """
    print("== buttons: environment check ==")
    ok = True

    ignore_py = os.environ.get("BUTTONS_IGNORE_PYTHON_CHECK")
    if ignore_py:
        print(
            "BUTTONS_IGNORE_PYTHON_CHECK set; skipping Python "
            "version failure"
        )
        ok &= True
    else:
        ok &= check_python()

    ok &= check_module("skidl")
    ok &= check_module("pytest")
    ok &= check_module("jinja2")
    # Prefer the CLI interface and avoid flags that may launch the GUI.
    run_cmd(["kicad-cli", "--version"])
    run_cmd(["kicad", "--version"])
    git_sha_short()
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())

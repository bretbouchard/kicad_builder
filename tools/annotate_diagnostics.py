#!/usr/bin/env python3
"""Create GitHub Actions annotations from auto-register diagnostics.

This script reads any `auto_register_diagnostics.json` files and prints
GitHub workflow commands (eg. `::error file=...,line=...::message`) so the
annotations appear in the Checks UI. The script never fails (exit 0) so it can
be used as a best-effort annotator in CI before a failing collector step runs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Dict, Any


def find_diagnostics(root: Path) -> Iterable[Path]:
    return root.glob("**/auto_register_diagnostics.json")


def emit_annotation(fp: Path, entry: Dict[str, Any]) -> None:
    # prefer snippet start_line if present
    snippet = entry.get("snippet")
    line = None
    if isinstance(snippet, dict):
        # snippet may be a mapping with start_line
        line = snippet.get("start_line")
    file_path = entry.get("path", str(fp))
    level = "error"
    msg = entry.get("message", "auto-register failure")
    # include short type and truncated traceback head
    kind = entry.get("type", "")
    tb = entry.get("traceback")
    if tb:
        tb_head = tb.splitlines()[:3]
        msg = f"{kind}: {msg} -- {tb_head[0] if tb_head else ''}"
    else:
        msg = f"{kind}: {msg}"

    # Escape newlines in msg
    msg = msg.replace("\n", " -- ")

    if line:
        print(f"::{level} file={file_path},line={line}::{msg}")
    else:
        print(f"::{level} file={file_path}::{msg}")


def main() -> int:
    root = Path.cwd()
    for p in find_diagnostics(root):
        try:
            data = json.loads(p.read_text(encoding="utf8"))
        except Exception:
            continue
        for entry in data if isinstance(data, list) else []:
            emit_annotation(p, entry)

    # Always succeed; annotations are best-effort
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

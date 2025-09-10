#!/usr/bin/env python3
"""Collect and summarize auto-register diagnostics files.

Scans the workspace for any `auto_register_diagnostics.json` files, prints a
summary for CI logs, and exits with code 1 if any diagnostics are found.
This is intended to be used in CI to fail early and provide a concise report.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any


def find_diagnostics(root: Path) -> List[Path]:
    return list(root.glob("**/auto_register_diagnostics.json"))


def summarize(path: Path) -> Dict[str, Any]:
    """Read and summarize a diagnostics JSON file.

    Returns a dict with the file path and either an "error" key on
    read/parse failure or a "failures" mapping of failure-type -> count.
    """
    text = path.read_text(encoding="utf8")
    try:
        data = json.loads(text)
    except Exception as exc:
        return {"path": str(path), "error": f"read_error: {exc}"}

    counts: Dict[str, int] = {}
    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                key = "unknown"
            else:
                key = item.get("type", "unknown")
                if not isinstance(key, str):
                    key = str(key)
            counts[key] = counts.get(key, 0) + 1

    return {"path": str(path), "failures": counts}


def main() -> int:
    root = Path.cwd()
    found = find_diagnostics(root)
    if not found:
        print("No auto-register diagnostics found.")
        return 0

    print("Found auto-register diagnostics:")
    any_summary = []
    for p in found:
        s = summarize(p)
        any_summary.append(s)
        print(json.dumps(s, indent=2))

    print()
    print("CI Note: auto-register diagnostics were found; failing the build.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Scaffold generator for hardware projects.

Usage: python tools/scaffold.py NAME

Creates a minimal hardware project skeleton under
hardware/projects/NAME. Files are written only if missing.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Template

DAID_TMPL = "# DAID Metadata\n# Generated: {{ timestamp }}\n# Git SHA: {{ git_sha }}\n"


MAKEFILE_TMPL = (
    "# Makefile for {{ project_name }}\n"
    "DAID_TIMESTAMP := {{ timestamp }}\n"
    "DAID_GIT_SHA := {{ git_sha }}\n"
    "DAID_TOOL_VERSIONS := {{ tool_versions_json }}\n\n"
    ".PHONY: gen verify\n"
    "gen:\n"
    "{TAB}python -m hardware.projects.{{ project_name }}.gen.netlist\n"
    "{TAB}python -m hardware.projects.{{ project_name }}.gen.schematic\n\n"
    "verify:\n"
    "{TAB}pytest -q hardware/projects/{{ project_name }}/tests/\n"
)


CI_TMPL = "name: Hardware CI\non: [push]\n"


TEMPLATE_FILES = {
    "gen/netlist.py": """# Minimal netlist generator stub
print('netlist generator stub')
""",
    "tests/test_smoke.py": """def test_smoke():
    assert True
""",
    "README.md": "# Project scaffold\n",
}


def ensure_dir(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def write_if_missing(path: Path, content: str) -> None:
    if path.exists():
        return
    path.write_text(content, encoding="utf-8")


def git_sha_short() -> str:
    try:
        out = subprocess.check_output(
            [
                "git",
                "rev-parse",
                "--short",
                "HEAD",
            ],
            text=True,
        )
        return out.strip()
    except Exception:
        return "unknown"


def timestamp_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_project(name: str) -> None:
    root = Path("hardware") / "projects" / name
    root.mkdir(parents=True, exist_ok=True)

    for rel, content in TEMPLATE_FILES.items():
        p = root / rel
        ensure_dir(p.parent)
        write_if_missing(p, content)

    ensure_dir(root / "kicad")

    daid = {
        "timestamp": timestamp_utc(),
        "git_sha": git_sha_short(),
        "kicad_version": "9.0",
        "python_version": sys.version.split()[0],
    }

    mf = Template(MAKEFILE_TMPL).render(
        project_name=name,
        timestamp=daid["timestamp"],
        git_sha=daid["git_sha"],
        tool_versions_json=json.dumps(daid),
    )
    mf = mf.replace("{TAB}", "\t")
    write_if_missing(root / "Makefile", mf)

    wf_dir = Path(".github") / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)
    wf = Template(CI_TMPL).render()
    write_if_missing(wf_dir / "hw.yml", wf)

    print(f"Created project scaffold at {root}")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: tools/scaffold.py NAME")
        return 2
    make_project(argv[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

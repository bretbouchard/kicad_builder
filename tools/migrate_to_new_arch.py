"""Simple migration helper to move an existing project to the new generator layout.

This script is intentionally tiny and conservative. It copies the source tree to
the destination and leaves a small migration stamp file.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def migrate_project(src: str | Path, dest: str | Path) -> None:
    src_p = Path(src)
    dest_p = Path(dest)
    if not src_p.exists():
        raise SystemExit(f"source does not exist: {src}")
    if dest_p.exists():
        raise SystemExit(f"destination already exists: {dest}")

    shutil.copytree(src_p, dest_p)
    stamp = dest_p / ".migrated_to_kicad_builder"
    stamp.write_text("migrated\n")


def main(argv: list[str] | None = None) -> int:
    argv = argv or list(sys.argv[1:])
    if len(argv) != 2:
        print("usage: migrate_to_new_arch.py <src> <dest>")
        return 2
    migrate_project(argv[0], argv[1])
    print("migration complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

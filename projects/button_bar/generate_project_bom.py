"""Simple project-level BOM flow for the Button Bar project.

Usage:
  python generate_project_bom.py [--enrich]

This script copies `projects/button_bar/bom.csv` into the canonical
`tools/output/bom.csv` location and optionally runs the parts enrichment
lookup (`tools/scripts/lookup_parts.py`) if `--enrich` is supplied and a
Mouser API key is available in the environment.
"""

import argparse
import pathlib
import shutil
import subprocess
import sys


def main(enrich: bool = False) -> int:
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    src = repo_root / "projects" / "button_bar" / "bom.csv"
    out = repo_root / "tools" / "output" / "bom.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, out)
    print(f"Copied project BOM to {out}")

    # If the project provides a pinmap.json, ensure BOM rows include it in the
    # `mapping_file` column where blank so downstream tools can pick it up.
    pinmap = repo_root / "projects" / "button_bar" / "pinmap.json"
    if pinmap.exists():
        # read the file and rewrite output with mapping_file where empty
        text = out.read_text()
        lines = text.splitlines()
        if len(lines) >= 1:
            header = lines[0].split(",")
            try:
                idx = header.index("mapping_file")
            except ValueError:
                idx = None

            if idx is not None:
                new_lines = [lines[0]]
                for ln in lines[1:]:
                    if not ln.strip():
                        continue
                    parts = ln.split(",")
                    # extend parts if line has fewer columns than header
                    if len(parts) <= idx:
                        parts += [""] * (idx - len(parts) + 1)
                    if not parts[idx].strip():
                        parts[idx] = "pinmap.json"
                    new_lines.append(",".join(parts))

                out.write_text("\n".join(new_lines) + "\n")

    if enrich:
        # run the lookup_parts script to enrich the BOM (may read .env)
        cmd = [
            sys.executable,
            str(repo_root / "tools" / "scripts" / "lookup_parts.py"),
        ]
        try:
            subprocess.check_call(cmd)
            print("Enrichment completed")
        except subprocess.CalledProcessError:
            print("Enrichment failed; see output above", file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument(
        "--enrich",
        action="store_true",
        help="Run parts enrichment (requires API key)",
    )
    ns = p.parse_args()
    raise SystemExit(main(enrich=ns.enrich))

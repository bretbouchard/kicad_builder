#!/usr/bin/env python3
"""read_metadata.py

Simple helper to read part metadata JSON and print key=value pairs for Makefile use.
"""

import json
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: read_metadata.py part.metadata.json")
        raise SystemExit(1)
    p = Path(sys.argv[1])
    if not p.exists():
        raise SystemExit(f"file not found: {p}")
    d = json.loads(p.read_text())
    # optional schema check: prefer jsonschema if available for richer errors
    schema_p = Path(__file__).parent / "metadata_schema.json"
    if schema_p.exists():
        schema = json.loads(schema_p.read_text())
        try:
            import jsonschema  # type: ignore
        except Exception:
            # fallback to lightweight checks
            for k, v in d.items():
                if k in schema.get("properties", {}):
                    expected = schema["properties"][k]["type"]
                    if expected == "number" and not isinstance(v, (int, float)):
                        raise SystemExit(f"metadata.{k} must be a number")
                    if expected == "integer" and not isinstance(v, int):
                        raise SystemExit(f"metadata.{k} must be an integer")
        else:
            try:
                jsonschema.validate(instance=d, schema=schema)
            except Exception as e:
                raise SystemExit(f"metadata validation error: {e}")
    # print environment-like KEY=VALUE lines for Makefile eval
    for k in ("pad_w", "pad_l", "ep", "pitch", "pads_per_side", "name"):
        if k in d:
            print(f"{k.upper()}={d[k]}")


if __name__ == "__main__":
    main()

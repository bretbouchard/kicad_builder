#!/usr/bin/env python3
from __future__ import annotations

import sys
import json
import traceback
import importlib.util
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(
            "usage: _preflight_register_helper.py <module_name> <path>",
            file=sys.stderr,
        )
        return 2

    module_name = argv[1]
    path = argv[2]

    # repo root is three parents up from this helper module; also ensure
    # the current working directory is present so imports like `src.*`
    # resolve correctly when running under test harnesses.
    repo_root = Path(__file__).resolve().parents[3]
    cwd = Path.cwd()
    # Prepend both to sys.path, preferring the repo root.
    sys.path.insert(0, str(repo_root))
    if str(cwd) != str(repo_root):
        sys.path.insert(0, str(cwd))

    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            print("spec failure", file=sys.stderr)
            return 3
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]

        regs: list[str | None] = []

        def _stub_register(*args: object, **kwargs: object) -> None:
            name: str | None = None
            try:
                if len(args) > 0:
                    val = args[0]
                    if isinstance(val, str):
                        name = val
                else:
                    # mypy/pyd temporary: kwargs is object; use getattr
                    try:
                        val = kwargs.get("name")  # type: ignore[attr-defined]
                        if isinstance(val, str):
                            name = val
                    except Exception:
                        name = None
            except Exception:
                name = None
            regs.append(name)

        if hasattr(mod, "GENERATOR"):
            g = getattr(mod, "GENERATOR")
            try:
                _stub_register(g)
            except Exception:
                raise
        elif hasattr(mod, "register") and callable(getattr(mod, "register")):
            try:
                # prefer calling with the stub; fall back to no-arg if the
                # callable does not accept args
                try:
                    getattr(mod, "register")(_stub_register)
                except TypeError:
                    getattr(mod, "register")()
            except Exception:
                raise

        # on success print a small JSON summary to stdout
        sys.stdout.write(json.dumps({"registrations": regs}))
        return 0
    except SystemExit as se:
        print(str(se), file=sys.stderr)
        return 4
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

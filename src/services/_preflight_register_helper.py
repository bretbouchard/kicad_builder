#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import traceback
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
            # Try to extract the registered name and optional namespace so
            # callers can perform lazy registration under the correct key.
            name: str | None = None
            namespace: str | None = None
            try:
                if len(args) > 0:
                    val = args[0]
                    if isinstance(val, str):
                        name = val
                # kwargs may include 'name' or 'namespace'
                try:
                    kname = kwargs.get("name")  # type: ignore[attr-defined]
                    kns = kwargs.get("namespace")  # type: ignore[attr-defined]
                    if isinstance(kname, str):
                        name = kname
                    if isinstance(kns, str):
                        namespace = kns
                except Exception:
                    pass
            except Exception:
                name = None

            if name and namespace:
                regs.append(f"{namespace}:{name}")
            else:
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

        # on success print a small JSON summary to stdout containing the
        # discovered registration names (optionally namespaced).
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

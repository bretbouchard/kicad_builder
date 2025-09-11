#!/usr/bin/env python3
"""Helper invoked by auto-register to preflight a generator module.

This script imports a module file in isolation and reports any registration
side-effects it performs (for example, calling
`register(name, generator, namespace=...)`). It prints a small JSON object
to stdout with discovered registration names.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import traceback
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("usage: _preflight_register_helper.py <module_name> <path>", file=sys.stderr)
        return 2

    module_name = argv[1]
    path = argv[2]

    # Ensure imports resolve from repo root when running under test harnesses
    repo_root = Path(__file__).resolve().parents[3]
    cwd = Path.cwd()
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

        # Execute the module in the prepared module object
        spec.loader.exec_module(mod)

        regs: list[str | None] = []

        def _stub_register(*args: object, **kwargs: object) -> None:
            # Extract possible name/namespace from args/kwargs for tests
            name: str | None = None
            namespace: str | None = None
            try:
                if len(args) > 0:
                    val = args[0]
                    if isinstance(val, str):
                        name = val
                # kwargs may include 'name' or 'namespace'
                kname = kwargs.get("name")
                kns = kwargs.get("namespace")
                if isinstance(kname, str):
                    name = kname
                if isinstance(kns, str):
                    namespace = kns
            except Exception:
                name = None

            if name and namespace:
                regs.append(f"{namespace}:{name}")
            else:
                regs.append(name)

        # If module exposes a GENERATOR constant, try to stub-register it.
        if hasattr(mod, "GENERATOR"):
            g = getattr(mod, "GENERATOR")
            try:
                _stub_register(g)
            except Exception:
                raise
        # If module exposes a register() callable, call it with our stub
        elif hasattr(mod, "register") and callable(getattr(mod, "register")):
            try:
                try:
                    getattr(mod, "register")(_stub_register)
                except TypeError:
                    getattr(mod, "register")()
            except Exception:
                raise

        # Success: emit JSON with discovered registrations
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

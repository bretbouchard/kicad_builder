from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Iterable, List, Optional

# note: we import specific registry helpers lazily where needed to avoid
# import-time cycles with preflight subprocess work.

# Preflight import timeout (seconds) when checking modules in a subprocess
PREFLIGHT_IMPORT_TIMEOUT = 5


class AutoRegisterError(RuntimeError):
    """Raised when auto-registration finds one or more problems.

    The exception carries a `failures` attribute which is a list of dicts
    with the keys: `path`, `type`, and `message` for programmatic
    inspection.
    """

    def __init__(self, failures: List[Dict[str, Any]]):
        self.failures = failures
        msgs = [f"{f.get('path')}: {f.get('type')}: {f.get('message')}" for f in failures]
        msg_text = "Auto-registration found problems:\n"
        msg_text += "\n".join(msgs[:20])
        super(AutoRegisterError, self).__init__(msg_text)


def _module_name_for_path(path: Path) -> str:
    # Prefer package-like names for modules under known packages so that
    # relative imports inside modules work correctly when executed from a
    # file.
    parts = list(path.parts)
    if "src" in parts and "lib" in parts and "generators" in parts:
        stem = path.stem
        return f"src.lib.generators.{stem}"
    if "hardware" in parts and "gen" in parts:
        stem = path.stem
        return f"hardware.gen.{stem}"
    return path.stem


def _load_module_from_path(
    path: Path,
) -> tuple[Optional[ModuleType], Optional[str]]:
    """Try to load a module from a file path.

    Returns (module, None) on success. On failure returns (None,
    traceback_text) so callers can enrich diagnostics with the original
    exception context.
    """
    module_name = _module_name_for_path(path)

    # Run a lightweight preflight import in a subprocess to catch
    # import-time errors and hangs quickly. If the preflight fails we
    # capture stderr and return it as the traceback to enrich diagnostics.
    preflight_err = _preflight_import(path, module_name, PREFLIGHT_IMPORT_TIMEOUT)
    if preflight_err is not None:
        return None, preflight_err

    try:
        spec = importlib.util.spec_from_file_location(module_name, str(path))
        if spec is None or spec.loader is None:
            return None, "failed to create import spec"
        mod = importlib.util.module_from_spec(spec)
        # Ensure the module is inserted under the chosen name before exec so
        # relative imports and package context are available.
        sys.modules[module_name] = mod
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        return mod, None
    except Exception:
        return None, traceback.format_exc()


def _preflight_import(path: Path, module_name: str, timeout: int) -> Optional[str]:
    """Attempt to import the module in a subprocess.

    Returns None on success. On failure returns stderr text (traceback).
    """
    # Build a small import snippet to run in the subprocess.
    repo_root = Path(__file__).resolve().parents[3]
    code = (
        "import importlib.util, sys, os\n"
        f"sys.path.insert(0, {repr(str(repo_root))})\n"
        'spec = importlib.util.spec_from_file_location("%s", "%s")\n'
        "if spec is None or spec.loader is None:\n"
        "    raise SystemExit('spec failure')\n"
        "mod = importlib.util.module_from_spec(spec)\n"
        'sys.modules["%s"] = mod\n'
        "spec.loader.exec_module(mod)\n"
    ) % (
        module_name,
        str(path),
        module_name,
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return f"timeout after {timeout}s"

    if proc.returncode != 0:
        return proc.stderr or proc.stdout or f"returncode {proc.returncode}"

    return None


def _preflight_register(path: Path, module_name: str, timeout: int) -> tuple[Optional[str], List[str] | None]:
    """Attempt to perform a registration dry-run in a subprocess.

    The subprocess will import the module and, if it exposes a `GENERATOR`
    or a `register` callable, attempt to call the registration entrypoint(s)
    while using a stub `register` function that captures calls. This lets
    us detect registration-time exceptions and hangs without mutating the
    parent process registry.

    Returns None on success. On failure returns stderr text (traceback).
    """
    # Call a small helper script to perform the registration dry-run. This
    # avoids embedding a large Python snippet as a string and reduces the
    # likelihood of quoting/indentation errors.
    helper = Path(__file__).resolve().parent / "_preflight_register_helper.py"
    try:
        proc = subprocess.run(
            [sys.executable, str(helper), module_name, str(path)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return f"timeout after {timeout}s", None

    if proc.returncode != 0:
        msg = proc.stderr or proc.stdout or f"returncode {proc.returncode}"
        return msg, None

    # parse stdout JSON for discovered registrations
    registrations: List[str] = []
    try:
        out = proc.stdout or ""
        if out:
            parsed = json.loads(out)
            if isinstance(parsed, dict) and "registrations" in parsed:
                maybe = parsed["registrations"]
                if isinstance(maybe, list):
                    registrations = [str(x) for x in maybe]
    except Exception:
        registrations = []

    return None, registrations


def discover_generator_files(paths: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        if not p.exists():
            continue
        if p.is_dir():
            for child in p.iterdir():
                if child.suffix == ".py" and child.is_file():
                    files.append(child)
        elif p.suffix == ".py":
            files.append(p)
    return files


def auto_register_generators(
    search_paths: Iterable[Path] | None = None,
    diagnostics_path: Optional[Path] = None,
) -> None:
    """Discover and register generators from common locations.

    Search locations (in order): `src/lib/generators` and `hardware/gen`.
    For each module, try to import it and register any exported `GENERATOR`
    attribute or a `register` callable.
    """
    candidates = [Path("src/lib/generators"), Path("hardware/gen")]
    if search_paths is not None:
        candidates = list(search_paths)
    files = discover_generator_files(candidates)
    failures: List[Dict[str, Any]] = []
    for f in files:
        mod, tb = _load_module_from_path(f)
        if mod is None:
            entry: Dict[str, Any] = {
                "path": str(f),
                "type": "import",
                "message": "failed to import",
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            if tb:
                entry["traceback"] = tb
                # try to extract a lineno and a code snippet from tb
                try:
                    import re

                    m = re.search(
                        r"File \"(?P<file>.+?)\", line (?P<line>\d+)",
                        tb,
                    )
                    if m:
                        tb_file = m.group("file")
                        tb_line = int(m.group("line"))
                        # if the traceback points at this file, extract snippet
                        if Path(tb_file).resolve() == f.resolve():
                            src = f.read_text(encoding="utf8").splitlines()
                            start = max(1, tb_line - 3)
                            end = min(len(src), tb_line + 2)
                            snippet_lines = src[start - 1 : end]
                            entry["snippet"] = {
                                "start_line": start,
                                "lines": snippet_lines,
                            }
                        else:
                            # include a small head of the file for context
                            src = f.read_text(encoding="utf8").splitlines()
                            head = src[:5]
                            entry["snippet"] = {"start_line": 1, "lines": head}
                except Exception:
                    # non-fatal: don't prevent collecting the main failure
                    pass
            failures.append(entry)
            continue
        # Prefer explicit registration entrypoints.
        # Determine whether the module exposes a GENERATOR symbol or a
        # register(register) callable so we can scope the preflight
        # registration run and correctly classify failures.
        has_generator = hasattr(mod, "GENERATOR")
        has_register_callable = hasattr(mod, "register") and callable(getattr(mod, "register"))

        # Only attempt a preflight registration dry-run if the module actually
        # exposes a registration entrypoint; this avoids running the helper for
        # modules that simply export constants.
        if has_generator or has_register_callable:
            try:
                preflight_err, registrations = _preflight_register(
                    f, _module_name_for_path(f), PREFLIGHT_IMPORT_TIMEOUT
                )
                if preflight_err is not None:
                    failures.append(
                        {
                            "path": str(f),
                            # classify the failure according to the entrypoint
                            "type": ("register_callable" if has_register_callable else "register"),
                            # surface the underlying stderr so callers can see
                            # the real exception message (e.g. "boom")
                            "message": preflight_err,
                            "ts": datetime.now(timezone.utc).isoformat(),
                            "traceback": preflight_err,
                        }
                    )
                    continue
            except Exception as exc:
                failures.append(
                    {
                        "path": str(f),
                        "type": ("register_callable" if has_register_callable else "register"),
                        "message": f"preflight registration error: {exc}",
                        "ts": datetime.now(timezone.utc).isoformat(),
                    }
                )
                continue

        if has_generator:
            g = getattr(mod, "GENERATOR")
            register_name = getattr(g, "name", f.stem)
            # register a lazy proxy so the module is imported later on demand
            try:
                from src.lib.generator_registry import register_lazy

                module_path = _module_name_for_path(f)
                # GENERATOR is a module-level symbol. Register the attribute
                # name explicitly so the lazy loader can retrieve it on import.
                register_lazy(register_name, module_path, "GENERATOR")
            except Exception as exc:
                tb_text = traceback.format_exc()
                entry = {
                    "path": str(f),
                    "type": "register",
                    "message": str(exc),
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "traceback": tb_text,
                }
                failures.append(entry)
        elif has_register_callable:
            # for modules that expose a register(register) callable we register
            # a lazy proxy that will import the module and call its register
            # implementation on first use (via the LazyGenerator wrapper).
            try:
                from src.lib.generator_registry import register_lazy

                module_path = _module_name_for_path(f)
                # Prefer registering lazy placeholders under the names the
                # module claims during its dry-run registration. If the
                # preflight helper returned discovered registration names
                # (e.g. ["vendor:example"]) register_lazy for each name so
                # lookups using the public name succeed without eager import.
                if registrations:
                    for name in registrations:
                        register_lazy(name, module_path, "register")
                else:
                    # fallback: use filename stem as the public name
                    register_lazy(f.stem, module_path, "register")
            except Exception as exc:
                tb_text = traceback.format_exc()
                entry = {
                    "path": str(f),
                    "type": "register_callable",
                    "message": str(exc),
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "traceback": tb_text,
                }
                failures.append(entry)
        else:
            failures.append(
                {
                    "path": str(f),
                    "type": "no_entrypoint",
                    "message": ("module does not export GENERATOR or register()"),
                    "ts": datetime.now(timezone.utc).isoformat(),
                }
            )

    if failures:
        # Optionally write structured diagnostics for CI or tooling.
        if diagnostics_path is not None:
            try:
                diagnostics_path.parent.mkdir(parents=True, exist_ok=True)
                diagnostics_path.write_text(json.dumps(failures, indent=2), encoding="utf8")
            except Exception:
                # Don't mask the primary error if diagnostics writing fails.
                pass

        # Surface structured failures via AutoRegisterError
        # (provides a `failures` list for programmatic checks)
        raise AutoRegisterError(failures)

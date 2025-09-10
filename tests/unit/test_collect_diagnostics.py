import json
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "tools" / "collect_diagnostics.py").exists():
            return parent
    # fallback
    return Path(__file__).resolve().parents[3]


def test_collector_finds_and_reports(tmp_path):
    # create a sample diagnostics file in the temp dir
    diag = tmp_path / "auto_register_diagnostics.json"
    sample = [
        {"path": "src/lib/generators/bad.py", "type": "import", "message": "failed"},
        {"path": "src/lib/generators/bad2.py", "type": "register", "message": "boom"},
    ]
    diag.write_text(json.dumps(sample))

    repo = _repo_root()
    script = repo / "tools" / "collect_diagnostics.py"

    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=tmp_path,  # collector uses cwd to find diagnostics
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 1
    assert "Found auto-register diagnostics" in proc.stdout
    assert "register" in proc.stdout
    assert "import" in proc.stdout


def test_collector_no_diagnostics(tmp_path):
    repo = _repo_root()
    script = repo / "tools" / "collect_diagnostics.py"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "No auto-register diagnostics found" in proc.stdout

import json
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "tools" / "annotate_diagnostics.py").exists():
            return parent
    return Path(__file__).resolve().parents[3]


def test_annotator_emits_annotations(tmp_path, capsys):
    diag = tmp_path / "auto_register_diagnostics.json"
    sample = [{"path": "src/lib/generators/bad.py", "type": "import", "message": "failed"}]
    diag.write_text(json.dumps(sample))

    repo = _repo_root()
    script = repo / "tools" / "annotate_diagnostics.py"

    proc = subprocess.run([sys.executable, str(script)], cwd=tmp_path, capture_output=True, text=True)

    assert proc.returncode == 0
    assert "::error" in proc.stdout

import subprocess
from pathlib import Path


def test_generate_bom_creates_csv(tmp_path):
    repo_root = Path(__file__).resolve().parents[2]
    out = repo_root / "tools" / "output" / "bom.csv"
    # remove if exists
    if out.exists():
        out.unlink()

    subprocess.check_call(["python3", str(repo_root / "tools" / "scripts" / "generate_bom.py")])
    assert out.exists(), "Expected bom.csv to be generated"
    text = out.read_text()
    assert "RP2040" in text, "Expected RP2040 to appear in BOM"

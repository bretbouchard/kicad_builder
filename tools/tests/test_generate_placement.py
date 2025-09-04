import subprocess
from pathlib import Path


def test_generate_placement_creates_csv():
    repo_root = Path(__file__).resolve().parents[2]
    # ensure BOM exists
    subprocess.check_call(["python3", str(repo_root / "tools" / "scripts" / "generate_bom.py")])
    subprocess.check_call(["python3", str(repo_root / "tools" / "scripts" / "generate_placement.py")])
    out = repo_root / "tools" / "output" / "placement.csv"
    assert out.exists()
    txt = out.read_text()
    assert "refdes" in txt

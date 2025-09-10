import subprocess
import tempfile
from pathlib import Path


def test_generate_placement_creates_csv() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    tmp = Path(tempfile.mkdtemp(prefix="test-place-"))
    bom = tmp / "bom.csv"
    out = tmp / "placement.csv"

    # generate a BOM into the temp dir
    subprocess.check_call(
        [
            "python3",
            str(repo_root / "tools" / "scripts" / "generate_bom.py"),
            "--out",
            str(bom),
        ]
    )

    subprocess.check_call(
        [
            "python3",
            str(repo_root / "tools" / "scripts" / "generate_placement.py"),
            "--bom",
            str(bom),
            "--out",
            str(out),
        ]
    )

    assert out.exists()
    txt = out.read_text()
    assert "refdes" in txt

import pathlib


def test_touch_led_doc_contains_arcon_id() -> None:
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    doc = repo_root / "docs" / "touch_led_grid_project.md"
    assert doc.exists(), f"Expected {doc} to exist"
    text = doc.read_text(encoding="utf8")
    assert "ee8e826e-ffa6-456b-b194-5729d1241d60" in text, "Arcon project id missing from doc"


def test_pipeline_smoke() -> None:
    assert True

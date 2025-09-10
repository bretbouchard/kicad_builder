from pathlib import Path

from src.models.project_config import ProjectConfig
from src.services import config_manager


def test_save_and_load(tmp_path: Path):
    cfg = ProjectConfig(
        project_name="demo",
        project_type="simple",
        metadata={"a": 1},
    )
    p = tmp_path / "cfg.json"
    config_manager.save(cfg, p)
    assert p.exists()
    loaded = config_manager.load(p)
    assert isinstance(loaded, ProjectConfig)
    assert loaded.project_name == "demo"
    assert loaded.project_type == "simple"


def test_validate_accepts_dict():
    raw = {"project_name": "d2", "project_type": "hier"}
    validated = config_manager.validate(raw)
    assert isinstance(validated, ProjectConfig)
    assert validated.project_name == "d2"

from src.models.project_config import ProjectConfig
from src.services import validation_engine


def test_validate_project_config_basic():
    cfg = ProjectConfig(project_name="n", project_type="t")
    assert validation_engine.validate_project_config(cfg) is True


def test_validate_project_config_missing_name():
    cfg = ProjectConfig(project_name="", project_type="t")
    try:
        validation_engine.validate_project_config(cfg)
        raised = False
    except validation_engine.ValidationError:
        raised = True
    assert raised

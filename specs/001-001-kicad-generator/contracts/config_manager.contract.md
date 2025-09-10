# Config Manager Contract

This contract specifies the expected behavior for `src.services.config_manager`.

Required behavior:
- `load(path)` must return a validated `src.models.project_config.ProjectConfig` instance or raise `ConfigManagerError` on failure.
- `save(config, path)` must persist JSON representation of the config. When passed a `ProjectConfig` instance it must prefer `model_dump` (pydantic v2) when available.
- `validate(data)` must accept dicts or ProjectConfig instances and return a validated ProjectConfig object.

Test notes:
- See tests/contract/test_config_manager_contract.py
# Config Manager Contract

Interface: ConfigManager

- load(path: str) -> ProjectConfig
- save(config: ProjectConfig, path: str) -> None
- validate(config: ProjectConfig) -> ValidationResult

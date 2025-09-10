# Generator Contract

This contract defines the minimal public interface and behavioral expectations for a KiCad generator plugin.

Required API:
- A generator must be either a subclass or an instance compatible with `src.lib.base_generator.BaseGenerator`.
- Provide a stable `name: str` attribute identifying the generator.
- Implement `generate(self, config: Any, out_dir: pathlib.Path) -> pathlib.Path` which creates artifacts and returns the output directory/path.
- Implement `validate(self, config: Any) -> bool` which returns True when the provided config is valid for this generator.
- Optionally implement `get_dependencies(self) -> list[str]`.

Behavioral guarantees:
- `generate` should fail loudly (raise) on misconfiguration.
- `validate` should perform deterministic checks and return boolean only (no side-effects).
- Generators registered into the registry must be detectable by namespace:name pattern and raise on duplicates.

Test notes:
- See tests/contract/test_generator_contract.py for the enforcement test skeleton.
# Generator Contract

Interface: Generator

- generate(config: ProjectConfig) -> Path
- validate(config: ProjectConfig) -> ValidationResult
- get_dependencies() -> list[str]

Behavior: Implementations must accept ProjectConfig and produce a KiCad project directory.

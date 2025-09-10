
# Generators

This folder contains small generator modules that can be auto-discovered by
the project's auto-registration service.


## Plugin contract (strict)

A few rules we enforce:

- A module must either export an instance named `GENERATOR` or provide a
  `register(registry)` callable.
- If exporting `GENERATOR`, the object should be a `BaseGenerator` instance
  and expose a `name` attribute (used to register under that name).
- The registry supports optional namespacing using `namespace:name` keys.


Auto-registration will fail-fast and raise a RuntimeError if any discovered
module cannot be imported or does not follow the contract. This ensures CI
fails early for broken plugins.


### Example (exporting instance)

```python
from src.lib.generators.template_generator import GENERATOR
```


### Example (register function)

```python
def register(registry):
    registry.register(
        "mygen",
        MyGenerator(),
        namespace="vendor",
    )
```

Generator contract

Purpose
-------
This folder holds pluggable generators. Each generator module must be explicit
and easy for CI to validate.

Contract (strict)
------------------
Each generator module MUST export one of the following:

1. `GENERATOR` — an instance of a class with a `generate(config, out_dir)` and
   `validate(config)` methods. The `GENERATOR` object should expose a `name`
   attribute used as the registration key.

2. `def register(registry)` — a callable that accepts a registry object and
   calls `registry.register(name, obj)` to register one or more generators.

Rules
-----
- Do not perform heavy work on import. Only construct lightweight metadata or
  factory objects.
- Name collisions are considered errors. Use unique generator names.
- Keep generators deterministic: given the same `ProjectConfig`, outputs must
  be byte-for-byte identical.

Example
-------
```python
from src.lib.base_generator import BaseGenerator

class MyGen(BaseGenerator):
    def __init__(self):
        super().__init__(name="mygen")

    def generate(self, config, out_dir):
        # write outputs
        return out_dir

    def validate(self, config):
        return True

# Export the instance so auto-registration picks it up
GENERATOR = MyGen()
```

CI behavior
-----------
- CI imports `src.cli` which runs auto-registration. If any generator module fails
  to import or does not expose `GENERATOR` or `register()`, CI will fail with a
  helpful message.


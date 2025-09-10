How to write a generator
========================

This short HOWTO explains the generator module contract, examples, and how to
write tests that exercise auto-registration safely.

Contract (strict)
------------------

- A generator module must either export an instance named `GENERATOR` (a
  `BaseGenerator` instance) or provide a `register(registry)` callable.
- If you export `GENERATOR`, the object should expose a `name` attribute used
  as the registration key.
- If you provide `register(registry)`, note that the auto-registerer passes
  the registry's `register` function (callable). Call it like:

    registry("myname", MyGenerator(), namespace="vendor")

Authoring tips
--------------

- Do not perform heavy work on import. Only construct lightweight metadata or
  the `GENERATOR` instance. Heavy operations should happen in `generate()`.
- Prefer simple module layout and a clear `name` on the generator for
  discoverability.

Example: export instance
------------------------

```python
from src.lib.base_generator import BaseGenerator
from pathlib import Path

class MyGen(BaseGenerator):
    def __init__(self):
        super().__init__(name="mygen")

    def generate(self, cfg, out_dir: Path) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        p = out_dir / "hello.txt"
        p.write_text("hello\n", encoding="utf8")
        return out_dir

GENERATOR = MyGen()
```

Example: register function
--------------------------

```python
def register(registry):
    registry("example", MyGen(), namespace="vendor")
```

Testing generators and auto-registration
----------------------------------------

- Unit tests: call generator classes directly (avoid import-time auto-registration).
- Integration tests: if you want to test auto-registration, run them in an
  isolated environment or point the auto-registerer to a temporary directory
  (the service supports `search_paths` for this reason).

  Example (in a pytest test):

```py
from src.services import auto_register
from src.lib import generator_registry

generator_registry.clear_registry()
auto_register.auto_register_generators(search_paths=[tmp_path])
```

CI notes
--------

The project's CI imports `src.cli` which triggers auto-registration. The
auto-registerer is strict: CI will fail if any discovered module is broken or
non-compliant. Use `search_paths` in tests to avoid scanning the entire repo
when you only want to exercise sample generators.

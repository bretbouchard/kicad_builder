# Plugin System Contract

Interface: PluginSystem

- discover(path: str) -> list[Plugin]
- load(name: str) -> Plugin
- register(plugin: Plugin) -> None

Structured failures & diagnostics:

- When auto-registration fails, the service will raise
	`src.services.auto_register.AutoRegisterError`.

- The exception exposes a `failures` attribute: a list of objects with the
	keys `path`, `type`, and `message` where `type` is one of
	`import`, `no_entrypoint`, `register`, or `register_callable`.

- `auto_register_generators` accepts an optional `diagnostics_path` parameter
	(a `pathlib.Path`). If provided, the service will write a JSON file
	containing the `failures` list for CI or tooling to consume. Failure to
	write diagnostics will not mask the primary registration error.

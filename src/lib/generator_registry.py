from __future__ import annotations

from threading import RLock
from typing import Any, Dict, List, Optional


_registry: Dict[str, Any] = {}
_lock = RLock()


def _qualify(namespace: Optional[str], name: str) -> str:
    if namespace:
        return f"{namespace}:{name}"
    return name


def register(name: str, generator: Any, namespace: Optional[str] = None) -> None:
    """Register a generator by name (optionally namespaced).

    Raises RuntimeError if the name is already registered.
    """
    q = _qualify(namespace, name)
    with _lock:
        if q in _registry:
            raise RuntimeError(f"generator already registered: {q}")
        _registry[q] = generator


class LazyGenerator:
    """A lazy proxy for a generator object.

    Stores the importable module path and attribute name. The real
    generator is imported on first access and cached.
    """

    def __init__(
        self,
        module_path: str,
        attr: str,
        _description: Optional[str] = None,
        public_name: Optional[str] = None,
        call_register_on_load: bool = False,
    ):
        self.module_path = module_path
        self.attr = attr
        self._real = None
        self._description = _description
        self.public_name = public_name
        self.call_register_on_load = call_register_on_load

    def _load(self):
        if self._real is not None:
            return self._real
        # import on demand
        import importlib

        mod = importlib.import_module(self.module_path)

        # Special case: some modules expose a `register(register)` callable
        # (mutating the registry). For those we call the module's register
        # function on first access so behavior matches eager registration.
        if self.call_register_on_load and self.public_name:
            reg_fn = getattr(mod, "register", None)
            if not callable(reg_fn):
                raise RuntimeError("module does not expose a callable register()")

            # Remove our placeholder from the registry so the module's
            # register() can insert the real entry without conflict.
            global _lock, _registry, register
            with _lock:
                # only pop if we are the placeholder
                cur = _registry.get(self.public_name)
                if cur is self:
                    _registry.pop(self.public_name, None)

            # Call the module register function; it may accept a register
            # callable or no args.
            try:
                try:
                    reg_fn(register)
                except TypeError:
                    reg_fn()
            except Exception:
                # On failure, re-insert ourselves to avoid leaving the
                # registry in an unexpected state.
                with _lock:
                    _registry[self.public_name] = self
                raise

            # After register completes, the real generator should be present
            # under the same public_name. Cache and return it.
            with _lock:
                self._real = _registry.get(self.public_name)
            return self._real

        self._real = getattr(mod, self.attr)
        return self._real

    def __call__(self, *a: object, **k: object):
        real = self._load()
        return real(*a, **k)

    def __getattr__(self, item: str):
        real = self._load()
        return getattr(real, item)

    def __repr__(self) -> str:
        return f"<LazyGenerator {self.module_path}:{self.attr}>"


def register_lazy(name: str, module_path: str, attr: str, namespace: Optional[str] = None) -> None:
    """Register a lazy generator that imports the real object on first use.

    If `attr` == "register" the LazyGenerator will call the module's
    `register()` on first access so modules that expect to mutate the
    registry behave the same as eager registration.
    """
    call_register = attr == "register"
    lg = LazyGenerator(
        module_path,
        attr,
        public_name=name,
        call_register_on_load=call_register,
    )
    register(name, lg, namespace=namespace)


def namespace_register(namespace: str, name: str, generator: Any) -> None:
    """Convenience wrapper to register under a namespace."""
    register(name, generator, namespace=namespace)


def get(name: str) -> Optional[Any]:
    """Return the registered generator (class or instance) or None.

    The caller should pass the fully-qualified name (namespace:name) or simple
    name if un-namespaced.
    """
    with _lock:
        return _registry.get(name)


def list_generators() -> List[str]:
    """Return list of registered generator names."""
    with _lock:
        return list(_registry.keys())


def clear_registry() -> None:
    """Clear all registered generators (useful for tests)."""
    with _lock:
        _registry.clear()

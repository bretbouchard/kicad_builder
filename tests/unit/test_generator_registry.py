from pathlib import Path

from src.lib import generator_registry as registry


def test_namespace_register_and_duplicate_detection(tmp_path: Path) -> None:
    registry.clear_registry()

    class Dummy:
        pass

    registry.register("foo", Dummy(), namespace=None)
    assert "foo" in registry.list_generators()

    # namespaced registration
    registry.register("bar", Dummy(), namespace="ns")
    assert "ns:bar" in registry.list_generators()

    # duplicate should raise
    try:
        registry.register("foo", Dummy(), namespace=None)
        raise AssertionError("expected duplicate registration to raise")
    except RuntimeError:
        pass

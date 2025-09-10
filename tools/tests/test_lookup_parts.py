import importlib.util
import os
import pathlib
import sys
import types

import pytest

# Ensure we load the lookup_parts module by path to avoid import issues when
# pytest is executed from different working directories or venvs used by
# pre-commit hooks. This keeps the test hermetic.
repo_root = pathlib.Path(__file__).resolve().parents[2]
lookup_path = repo_root / "tools" / "scripts" / "lookup_parts.py"
spec = importlib.util.spec_from_file_location("lookup_parts", str(lookup_path))
assert spec is not None and spec.loader is not None
lookup_parts = importlib.util.module_from_spec(spec)
sys.modules["lookup_parts"] = lookup_parts
spec.loader.exec_module(lookup_parts)


def test_query_with_retries_mock(monkeypatch):
    """Ensure query_with_retries returns a parsed response when mouser_search
    yields a product list (monkeypatched)."""

    def fake_mouser_search(api_key: str, query: str):
        return {
            "SearchResults": {
                "Products": [
                    {
                        "ManufacturerPartNumber": "PN1",
                        "Description": "10k resistor",
                        "Manufacturer": "ACME",
                    }
                ]
            }
        }

    monkeypatch.setattr(lookup_parts, "mouser_search", fake_mouser_search)

    resp = lookup_parts.query_with_retries("fakekey", ["resistor 10k"])
    assert resp is not None
    assert "SearchResults" in resp


def test_mouser_search_mock_requests(monkeypatch):
    """Monkeypatch the requests.get path used by mouser_search so the
    function exercises the requests branch without network access."""

    class FakeResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "Products": [
                    {
                        "ManufacturerPartNumber": "PN2",
                        "Description": "10k resistor",
                        "Manufacturer": "ACME",
                    }
                ]
            }

    def fake_get(url, params=None, timeout=None):
        return FakeResp()

    # patch the module-level requests object used in lookup_parts
    monkeypatch.setattr(lookup_parts, "requests", types.SimpleNamespace(get=fake_get))

    resp = lookup_parts.mouser_search("fakekey", "resistor 10k")
    assert resp is not None
    assert resp.get("Products") or resp.get("SearchResults", {}).get("Products")


def test_live_mouser_lookup_integration():
    """Optional integration test that runs against the real Mouser API when an
    API key is present in the environment. Skips otherwise so CI is safe.
    """

    api_key = os.environ.get("mouser_api_key") or os.environ.get("MOU_SER_API_KEY")
    if not api_key:
        pytest.skip("no mouser API key in environment")

    # Use a very common query and minimal retries so this test is fast.
    resp = lookup_parts.query_with_retries(
        str(api_key),
        ["resistor 10k"],
        max_retries=1,
        backoff_base=0.1,
        rate_limit_delay=0,
    )
    assert resp is not None
    products = resp.get("SearchResults", {}).get("Products") or resp.get("Products")
    assert products and len(products) > 0

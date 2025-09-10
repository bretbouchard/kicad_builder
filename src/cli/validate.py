from __future__ import annotations

import argparse

from src.services.config_manager import load as load_config
from src.services.validation_engine import ValidationError, validate_project_config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="kb-validate")
    parser.add_argument("--config", required=True, help="Path to project config JSON")
    args = parser.parse_args(argv)

    try:
        cfg = load_config(args.config)
    except Exception as exc:
        print(f"error loading config: {exc}")
        return 2

    try:
        validate_project_config(cfg)
        print("VALID")
        return 0
    except ValidationError as exc:
        print(f"INVALID: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

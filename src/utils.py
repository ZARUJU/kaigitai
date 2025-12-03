from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    # src/utils.py -> src -> repo_root
    return Path(__file__).resolve().parent.parent


def register_dir() -> Path:
    return repo_root() / "register"


def data_dir() -> Path:
    return repo_root() / "data"


def schema_base_dir() -> Path:
    return repo_root() / "docs" / "schema" / "base"


def schema_fragment_dir() -> Path:
    return repo_root() / "docs" / "schema" / "fragment"

from __future__ import annotations

from pathlib import Path
from typing import Any

import jsonschema

from src.core.loader import load_json_file


def validate_with_schema(data: Any, schema_path: Path) -> None:
    schema = load_json_file(schema_path)
    jsonschema.validate(instance=data, schema=schema)

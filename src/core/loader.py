from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json


def load_json_file(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return json.loads(text)


def load_json_files(dir_path: Path, pattern: str = "*.json") -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for file in sorted(dir_path.glob(pattern)):
        data = load_json_file(file)
        results.append(data)
    return results

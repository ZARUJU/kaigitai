from __future__ import annotations

from pathlib import Path
from typing import List

from src.core.loader import load_json_files
from src.core.writer import write_json_file
from src.utils import data_dir, schema_fragment_dir


def _collect_names(dir_path: Path) -> List[str]:
    names: List[str] = []
    if not dir_path.exists():
        return names
    for obj in load_json_files(dir_path):
        name = obj.get("name")
        if name:
            names.append(name)
    return names


def run_fragment() -> None:
    fragments_dir = schema_fragment_dir()
    fragments_dir.mkdir(parents=True, exist_ok=True)

    group_names = _collect_names(data_dir() / "group")
    write_json_file(fragments_dir / "group_names.json", {"enum": group_names})

    person_names = _collect_names(data_dir() / "person")
    write_json_file(fragments_dir / "person_names.json", {"enum": person_names})

    print("fragment生成完了")

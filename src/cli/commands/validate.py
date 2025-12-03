from __future__ import annotations

from pathlib import Path

from src.core.loader import load_json_file, load_json_files
from src.core.validator import validate_with_schema
from src.utils import data_dir, register_dir, schema_base_dir


def run_validate() -> None:
    base = schema_base_dir()
    # register
    register_targets = [
        (register_dir() / "group" / "form.json", base / "group.register.schema.json"),
        (register_dir() / "person" / "form.json", base / "person.register.schema.json"),
        (register_dir() / "meeting" / "form.json", base / "meeting.basic.register.schema.json"),
    ]
    for path, schema in register_targets:
        if not path.exists():
            continue
        print(f"[validate register] {path}")
        payload = load_json_file(path)
        validate_with_schema(payload, schema)

    # data (group/person)
    data_targets = [
        (data_dir() / "group", base / "group.data.schema.json"),
        (data_dir() / "person", base / "person.data.schema.json"),
    ]
    for dir_path, schema in data_targets:
        if not dir_path.exists():
            continue
        schema_path = schema
        for obj in load_json_files(dir_path):
            validate_with_schema(obj, schema_path)

    # meeting basic
    meeting_dir = data_dir() / "meeting"
    schema_path = base / "meeting.basic.data.schema.json"
    if meeting_dir.exists():
        for sub in meeting_dir.iterdir():
            path = sub / "basic.json"
            if path.exists():
                payload = load_json_file(path)
                validate_with_schema(payload, schema_path)
                print(f"[validate data] {path}")

    print("検証完了")

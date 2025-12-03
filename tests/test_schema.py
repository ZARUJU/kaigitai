from __future__ import annotations

import json
from pathlib import Path

import jsonschema


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(data: dict, schema_path: Path) -> None:
    schema = _load_json(schema_path)
    jsonschema.validate(instance=data, schema=schema)


def test_register_forms_validate() -> None:
    base = Path("docs/schema/base")
    targets = [
        (Path("register/group/form.json"), base / "group.register.schema.json"),
        (Path("register/person/form.json"), base / "person.register.schema.json"),
        (Path("register/meeting/form.json"), base / "meeting.basic.register.schema.json"),
    ]
    for data_path, schema_path in targets:
        data = _load_json(data_path)
        schema = _load_json(schema_path)
        jsonschema.validate(instance=data, schema=schema)


def test_data_schemas_accept_minimal_payloads() -> None:
    base = Path("docs/schema/base")

    group = {
        "id": "g-1",
        "name": "G",
        "category": "cat",
        "official_url": "https://example.com",
        "parent": None,
        "list_url": None,
    }
    _validate(group, base / "group.data.schema.json")

    person = {"id": "p-1", "name": "P", "name_yomi": None}
    _validate(person, base / "person.data.schema.json")

    meeting = {
        "id": "m-1",
        "main": {"group_id": "g-1", "num": 1},
        "sub": [],
        "date": "2024-01-01",
        "holding": "onsite",
        "start_time": None,
        "end_time": None,
        "agenda": [],
        "attendee": [],
        "sources": [{"url": "https://example.com", "source_type": "meeting_page", "title": None}],
        "materials": [],
    }
    _validate(meeting, base / "meeting.basic.data.schema.json")

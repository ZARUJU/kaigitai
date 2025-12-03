from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from src.core.loader import load_json_file
from src.core.resolver import NameRegistry
from src.core.validator import validate_with_schema
from src.core.writer import write_json_file
from src.utils import data_dir, register_dir, schema_base_dir


@dataclass
class ConvertResult:
    created: int
    updated: int
    skipped: int = 0
    errors: List[str] = field(default_factory=list)
    planned: List[Path] = field(default_factory=list)


def _load_register(path: Path, schema: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    payload = load_json_file(path)
    validate_with_schema(payload, schema)
    assert isinstance(payload, list)
    return payload


def convert_group(dry_run: bool = False) -> tuple[NameRegistry, ConvertResult]:
    reg_path = register_dir() / "group" / "form.json"
    schema_path = schema_base_dir() / "group.register.schema.json"
    data_schema = schema_base_dir() / "group.data.schema.json"
    records = _load_register(reg_path, schema_path)
    name_to_id_list: List[Dict[str, str]] = []
    result = ConvertResult(created=0, updated=0)
    for rec in records:
        group_id = rec.get("id") or str(uuid4())
        output = {
            "id": group_id,
            "name": rec["name"],
            "parent": rec.get("parent"),
            "category": rec["category"],
            "list_url": rec.get("list_url"),
            "official_url": rec["official_url"],
        }
        validate_with_schema(output, data_schema)
        dest = data_dir() / "group" / f"{group_id}.json"
        if dry_run:
            result.planned.append(dest)
        else:
            result.updated += 1 if dest.exists() else 0
            result.created += 0 if dest.exists() else 1
            write_json_file(dest, output)
        name_to_id_list.append({"name": rec["name"], "id": group_id})
    return NameRegistry.from_lists(name_to_id_list), result


def convert_person(dry_run: bool = False) -> tuple[NameRegistry, ConvertResult]:
    reg_path = register_dir() / "person" / "form.json"
    schema_path = schema_base_dir() / "person.register.schema.json"
    data_schema = schema_base_dir() / "person.data.schema.json"
    records = _load_register(reg_path, schema_path)
    name_to_id_list: List[Dict[str, str]] = []
    result = ConvertResult(created=0, updated=0)
    for rec in records:
        person_id = rec.get("id") or str(uuid4())
        output = {
          "id": person_id,
          "name": rec["name"],
          "name_yomi": rec.get("name_yomi"),
        }
        validate_with_schema(output, data_schema)
        dest = data_dir() / "person" / f"{person_id}.json"
        if dry_run:
            result.planned.append(dest)
        else:
            result.updated += 1 if dest.exists() else 0
            result.created += 0 if dest.exists() else 1
            write_json_file(dest, output)
        name_to_id_list.append({"name": rec["name"], "id": person_id})
    return NameRegistry.from_lists(name_to_id_list), result


def convert_meeting(
    group_registry: NameRegistry,
    person_registry: NameRegistry,
    dry_run: bool = False,
    strict_missing: bool = True,
) -> ConvertResult:
    reg_path = register_dir() / "meeting" / "form.json"
    schema_path = schema_base_dir() / "meeting.basic.register.schema.json"
    data_schema = schema_base_dir() / "meeting.basic.data.schema.json"
    records = _load_register(reg_path, schema_path)
    result = ConvertResult(created=0, updated=0)
    for rec in records:
        meeting_id = rec.get("id") or str(uuid4())
        main = rec["main"]
        try:
            main_id = group_registry.resolve(main["group_id"])
            sub_list = []
            for sub in rec.get("sub", []):
                sub_list.append({
                  "group_id": group_registry.resolve(sub["group_id"]),
                  "num": sub["num"],
                })
            attendee_ids = [person_registry.resolve(a) for a in rec.get("attendee", [])]
        except ValueError as e:
            if strict_missing:
                raise
            result.skipped += 1
            result.errors.append(str(e))
            continue
        output = {
          "id": meeting_id,
          "main": {"group_id": main_id, "num": main["num"]},
          "sub": sub_list,
          "date": rec["date"],
          "holding": rec["holding"],
          "start_time": rec.get("start_time"),
          "end_time": rec.get("end_time"),
          "agenda": rec.get("agenda", []),
          "attendee": attendee_ids,
          "sources": rec.get("sources", []),
          "materials": rec.get("materials", []),
        }
        validate_with_schema(output, data_schema)
        dest = data_dir() / "meeting" / meeting_id / "basic.json"
        if dry_run:
            result.planned.append(dest)
        else:
            result.updated += 1 if dest.exists() else 0
            result.created += 0 if dest.exists() else 1
            write_json_file(dest, output)
    return result

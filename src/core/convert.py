from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from src.core.loader import load_json_file, load_json_files
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


def _load_existing_group_registry() -> Dict[str, str]:
    """既存data/groupの name→id を取得する."""
    group_dir = data_dir() / "group"
    if not group_dir.exists():
        return {}
    existing: Dict[str, str] = {}
    for rec in load_json_files(group_dir):
        name = rec.get("name")
        gid = rec.get("id")
        if not name or not gid:
            continue
        existing[NameRegistry._normalize(name)] = gid
    return existing


def convert_group(dry_run: bool = False) -> tuple[NameRegistry, ConvertResult]:
    reg_path = register_dir() / "group" / "form.json"
    schema_path = schema_base_dir() / "group.register.schema.json"
    data_schema = schema_base_dir() / "group.data.schema.json"
    records = _load_register(reg_path, schema_path)
    # 既存dataを先に取り込み、同名ならIDを再利用する
    name_to_id: Dict[str, str] = _load_existing_group_registry()
    prepared: List[Dict[str, Any]] = []
    result = ConvertResult(created=0, updated=0)
    for rec in records:
        norm_name = NameRegistry._normalize(rec["name"])
        # registerで明示IDがあれば優先、無ければ既存データのIDを流用、それも無ければ新規採番
        group_id = rec.get("id") or name_to_id.get(norm_name) or str(uuid4())
        name_to_id[norm_name] = group_id
        prepared.append({**rec, "id": group_id})

    registry = NameRegistry.from_lists([{"name": name, "id": gid} for name, gid in name_to_id.items()])

    for rec in prepared:
        parent_raw = rec.get("parent")
        parent_id = None
        if parent_raw:
            try:
                parent_id = registry.resolve(parent_raw)
            except ValueError as e:
                raise ValueError(f"親グループが未登録です: {parent_raw}") from e
        output = {
            "id": rec["id"],
            "name": rec["name"],
            "parent": parent_id,
            "category": rec["category"],
            "list_url": rec.get("list_url"),
            "official_url": rec["official_url"],
        }
        validate_with_schema(output, data_schema)
        dest = data_dir() / "group" / f"{rec['id']}.json"
        if dry_run:
            result.planned.append(dest)
        else:
            result.updated += 1 if dest.exists() else 0
            result.created += 0 if dest.exists() else 1
            write_json_file(dest, output)
    return registry, result


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

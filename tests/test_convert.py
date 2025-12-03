from __future__ import annotations

import json
import shutil
from pathlib import Path

import jsonschema

from src.core.convert import convert_group, convert_meeting, convert_person
import src.utils as utils


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(data: dict, schema_path: Path) -> None:
    schema = _load_json(schema_path)
    jsonschema.validate(instance=data, schema=schema)


def test_convert_register_to_data(monkeypatch, tmp_path: Path) -> None:
    # 準備：テンポラリに register/ と docs/schema/base をコピー
    repo_root = Path(__file__).resolve().parent.parent
    shutil.copytree(repo_root / "register", tmp_path / "register")
    shutil.copytree(repo_root / "docs" / "schema" / "base", tmp_path / "docs" / "schema" / "base")
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)

    # utils のパス関数を tmp_path を返すように差し替え
    monkeypatch.setattr(utils, "repo_root", lambda: tmp_path)

    # 変換を実行
    group_registry, _ = convert_group()
    person_registry, _ = convert_person()
    convert_meeting(group_registry, person_registry)

    # 出力確認とスキーマ検証
    base = tmp_path / "docs" / "schema" / "base"

    for file in (tmp_path / "data" / "group").glob("*.json"):
        _validate(_load_json(file), base / "group.data.schema.json")

    for file in (tmp_path / "data" / "person").glob("*.json"):
        _validate(_load_json(file), base / "person.data.schema.json")

    meeting_dir = tmp_path / "data" / "meeting"
    if meeting_dir.exists():
        for subdir in meeting_dir.iterdir():
            basic = subdir / "basic.json"
            _validate(_load_json(basic), base / "meeting.basic.data.schema.json")

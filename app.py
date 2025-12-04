from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from flask import Flask, redirect, render_template, request, url_for

from src.core.validator import validate_with_schema
from src.utils import data_dir, schema_base_dir

app = Flask(__name__)


# ========== helpers ==========


def _load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2)
    path.write_text(text, encoding="utf-8")


def _validate_data(entity: str, payload: Dict[str, Any]) -> None:
    base = schema_base_dir()
    schema_map = {
        "group": base / "group.data.schema.json",
        "person": base / "person.data.schema.json",
        "meeting": base / "meeting.basic.data.schema.json",
    }
    schema_path = schema_map[entity]
    validate_with_schema(payload, schema_path)


# ========== data access ==========


def load_groups() -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    dir_path = data_dir() / "group"
    for file in sorted(dir_path.glob("*.json")):
        data = _load_json(file, {})
        data["id"] = file.stem
        results.append(data)
    return sorted(results, key=lambda g: (g.get("name") or "", g["id"]))


def load_persons() -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    dir_path = data_dir() / "person"
    for file in sorted(dir_path.glob("*.json")):
        data = _load_json(file, {})
        data["id"] = file.stem
        results.append(data)
    return results


def load_meetings() -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    dir_path = data_dir() / "meeting"
    if not dir_path.exists():
        return results
    for folder in sorted(p for p in dir_path.iterdir() if p.is_dir()):
        basic = folder / "basic.json"
        data = _load_json(basic, {})
        data["id"] = folder.name
        results.append(data)
    def sort_key(m: Dict[str, Any]):
        return (m.get("date") or "", m.get("main", {}).get("num") or 0)
    return sorted(results, key=sort_key, reverse=True)


def save_group(group_id: str, payload: Dict[str, Any]) -> None:
    _validate_data("group", payload)
    _write_json(data_dir() / "group" / f"{group_id}.json", payload)


def save_person(person_id: str, payload: Dict[str, Any]) -> None:
    _validate_data("person", payload)
    _write_json(data_dir() / "person" / f"{person_id}.json", payload)


def save_meeting(meeting_id: str, payload: Dict[str, Any]) -> None:
    _validate_data("meeting", payload)
    _write_json(data_dir() / "meeting" / meeting_id / "basic.json", payload)


def delete_group(group_id: str) -> None:
    path = data_dir() / "group" / f"{group_id}.json"
    if path.exists():
        path.unlink()


def delete_person(person_id: str) -> None:
    path = data_dir() / "person" / f"{person_id}.json"
    if path.exists():
        path.unlink()


def delete_meeting(meeting_id: str) -> None:
    folder = data_dir() / "meeting" / meeting_id
    if folder.exists():
        shutil.rmtree(folder)


# ========== parsing helpers for meeting form ==========


def _parse_sub_lines(raw: str) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 2:
            raise ValueError("sub は 1行ごとに group_id,num で入力してください")
        items.append({"group_id": parts[0], "num": int(parts[1])})
    return items


def _parse_attendees(raw: str) -> List[str]:
    return [line.strip() for line in raw.splitlines() if line.strip()]


def _parse_agenda(raw: str) -> List[str]:
    return [line.strip() for line in raw.splitlines() if line.strip()]


def _parse_sources(raw: str) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 1:
            continue
        url = parts[0]
        source_type = parts[1] if len(parts) > 1 and parts[1] else "other"
        title = parts[2] if len(parts) > 2 and parts[2] else None
        items.append({"url": url, "source_type": source_type or "other", "title": title})
    return items


def _parse_materials(raw: str) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        url = parts[0]
        title = parts[1] if len(parts) > 1 and parts[1] else None
        items.append({"url": url, "title": title})
    return items


# ========== routes ==========


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def index() -> str:
    return render_template("index.html")


# ---- group ----


@app.get("/group")
def group_list() -> str:
    groups = load_groups()
    return render_template("group_list.html", groups=groups)


def _build_group_tree(level_limit: Optional[int] = None) -> tuple[List[Dict[str, Any]], int]:
    groups = load_groups()
    by_parent: Dict[Optional[str], List[Dict[str, Any]]] = {}
    for g in groups:
        by_parent.setdefault(g.get("parent"), []).append(g)

    def build(parent_id: Optional[str], depth: int) -> List[Dict[str, Any]]:
        nodes: List[Dict[str, Any]] = []
        for child in by_parent.get(parent_id, []):
            # depthが制限に達したら子は展開しない
            children = [] if (level_limit and depth >= level_limit) else build(child["id"], depth + 1)
            nodes.append({"data": child, "children": children})
        return nodes

    def calc_depth(parent_id: Optional[str], depth: int) -> int:
        children = by_parent.get(parent_id, [])
        if not children:
            return depth
        return max(calc_depth(child["id"], depth + 1) for child in children)

    roots = build(None, 1)
    max_depth = 0
    if by_parent.get(None):
        max_depth = max(calc_depth(root["id"], 1) for root in by_parent[None])
    return roots, max_depth


@app.get("/group/tree")
def group_tree() -> str:
    tree, max_level = _build_group_tree()
    return render_template("group_tree.html", tree=tree, level=None, max_level=max_level)


@app.get("/group/tree/<int:level>")
def group_tree_level(level: int) -> str:
    level_limit = level if level > 0 else None
    tree, max_level = _build_group_tree(level_limit)
    return render_template("group_tree.html", tree=tree, level=level_limit, max_level=max_level)


@app.get("/group/new")
def group_new() -> str:
    groups = load_groups()
    return render_template("group_form.html", group={}, mode="new", groups=groups)


@app.post("/group/new")
def group_create() -> str:
    form = request.form
    group_id = str(uuid4())
    payload = {
        "id": group_id,
        "name": form["name"].strip(),
        "parent": form.get("parent") or None,
        "category": form["category"].strip(),
        "list_url": form.get("list_url") or None,
        "official_url": form["official_url"].strip(),
    }
    try:
        save_group(group_id, payload)
        return redirect(url_for("group_detail", id=group_id))
    except Exception as e:  # noqa: BLE001
        groups = load_groups()
        return render_template("group_form.html", group=payload, mode="new", error=str(e), groups=groups)


@app.get("/group/<id>")
def group_detail(id: str) -> str:
    path = data_dir() / "group" / f"{id}.json"
    if not path.exists():
        return "not found", 404
    group = _load_json(path, {})
    group["id"] = id
    groups = load_groups()
    group_map = {g["id"]: g["name"] for g in groups}
    parent_label = "-"
    parent_id_for_link = None
    if group.get("parent"):
        parent_id = group["parent"]
        parent_name = next((g["name"] for g in groups if g.get("id") == parent_id), None)
        parent_label = f"{parent_name} ({parent_id})" if parent_name else parent_id
        parent_id_for_link = parent_id
    meetings = load_meetings()
    main_meetings = [m for m in meetings if m.get("main", {}).get("group_id") == id]
    sub_meetings = [
        m
        for m in meetings
        if any(sub.get("group_id") == id for sub in m.get("sub", []))
    ]
    return render_template(
        "group_detail.html",
        group=group,
        parent_label=parent_label,
        parent_id=parent_id_for_link,
        main_meetings=main_meetings,
        sub_meetings=sub_meetings,
        group_map=group_map,
    )


@app.get("/group/<id>/children")
def group_children(id: str) -> str:
    groups = load_groups()
    current = next((g for g in groups if g.get("id") == id), None)
    if current is None:
        return "not found", 404
    by_parent: Dict[Optional[str], List[Dict[str, Any]]] = {}
    for g in groups:
        by_parent.setdefault(g.get("parent"), []).append(g)

    def build(parent_id: Optional[str]) -> List[Dict[str, Any]]:
        nodes: List[Dict[str, Any]] = []
        for child in by_parent.get(parent_id, []):
            nodes.append({"data": child, "children": build(child["id"])})
        return nodes

    tree = build(id)
    return render_template("group_children.html", group=current, tree=tree)


@app.get("/group/<id>/edit")
def group_edit(id: str) -> str:
    path = data_dir() / "group" / f"{id}.json"
    if not path.exists():
        return "not found", 404
    group = _load_json(path, {})
    group["id"] = id
    groups = load_groups()
    return render_template("group_form.html", group=group, mode="edit", groups=groups)


@app.post("/group/<id>/edit")
def group_update(id: str) -> str:
    form = request.form
    payload = {
        "id": id,
        "name": form["name"].strip(),
        "parent": form.get("parent") or None,
        "category": form["category"].strip(),
        "list_url": form.get("list_url") or None,
        "official_url": form["official_url"].strip(),
    }
    try:
        save_group(id, payload)
        return redirect(url_for("group_detail", id=id))
    except Exception as e:  # noqa: BLE001
        groups = load_groups()
        return render_template("group_form.html", group=payload, mode="edit", error=str(e), groups=groups)


@app.post("/group/<id>/delete")
def group_delete(id: str) -> str:
    delete_group(id)
    return redirect(url_for("group_list"))


# ---- person ----


@app.get("/person")
def person_list() -> str:
    persons = load_persons()
    return render_template("person_list.html", persons=persons)


@app.get("/person/new")
def person_new() -> str:
    return render_template("person_form.html", person={}, mode="new")


@app.post("/person/new")
def person_create() -> str:
    form = request.form
    person_id = str(uuid4())
    payload = {
        "id": person_id,
        "name": form["name"].strip(),
        "name_yomi": form.get("name_yomi") or None,
    }
    try:
        save_person(person_id, payload)
        return redirect(url_for("person_detail", id=person_id))
    except Exception as e:  # noqa: BLE001
        return render_template("person_form.html", person=payload, mode="new", error=str(e))


@app.get("/person/<id>")
def person_detail(id: str) -> str:
    path = data_dir() / "person" / f"{id}.json"
    if not path.exists():
        return "not found", 404
    person = _load_json(path, {})
    person["id"] = id
    return render_template("person_detail.html", person=person)


@app.get("/person/<id>/edit")
def person_edit(id: str) -> str:
    path = data_dir() / "person" / f"{id}.json"
    if not path.exists():
        return "not found", 404
    person = _load_json(path, {})
    person["id"] = id
    return render_template("person_form.html", person=person, mode="edit")


@app.post("/person/<id>/edit")
def person_update(id: str) -> str:
    form = request.form
    payload = {
        "id": id,
        "name": form["name"].strip(),
        "name_yomi": form.get("name_yomi") or None,
    }
    try:
        save_person(id, payload)
        return redirect(url_for("person_detail", id=id))
    except Exception as e:  # noqa: BLE001
        return render_template("person_form.html", person=payload, mode="edit", error=str(e))


@app.get("/meeting")
def meeting_list() -> str:
    q = request.args.get("q", "").strip().lower()
    meetings = load_meetings()
    if q:
        meetings = [
            m for m in meetings
            if q in m.get("id", "").lower()
            or q in (m.get("date", "") or "").lower()
            or q in (str(m.get("main", {}).get("num", ""))).lower()
            or q in (m.get("holding", "") or "").lower()
        ]
    groups = load_groups()
    group_map = {g["id"]: g["name"] for g in groups}
    persons = load_persons()
    person_map = {p["id"]: p["name"] for p in persons}
    return render_template(
        "meeting_list.html",
        meetings=meetings,
        group_map=group_map,
        person_map=person_map,
        q=q,
    )


@app.get("/meeting/new")
def meeting_new() -> str:
    groups = load_groups()
    persons = load_persons()
    prefill_group = request.args.get("main_group_id", "").strip()
    meeting_prefill = {
        "main": {"group_id": prefill_group, "num": ""},
        "sub_group_id_list": ["" for _ in range(3)],
        "sub_num_list": ["" for _ in range(3)],
        "attendee_multi": [],
    }
    return render_template(
        "meeting_form.html",
        meeting=meeting_prefill,
        mode="new",
        groups=groups,
        persons=persons,
        error=None,
    )


def _extract_meeting_form(form) -> Dict[str, Any]:
    main_group_id = form["main_group_id"].strip()
    main_num = int(form["main_num"])
    agenda_raw = form.get("agenda_lines", "")
    sources_raw = form.get("sources_lines", "")
    materials_raw = form.get("materials_lines", "")

    attendees: List[str] = []
    if hasattr(form, "getlist"):
        attendees = [a.strip() for a in form.getlist("attendee_multi") if a.strip()]

    sub_pairs: List[Dict[str, Any]] = []
    if hasattr(form, "getlist"):
        gids = form.getlist("sub_group_id")
        nums = form.getlist("sub_num")
        for gid, num in zip(gids, nums):
            gid = gid.strip()
            if not gid:
                continue
            sub_pairs.append({"group_id": gid, "num": int(num)})
    if not sub_pairs:
        sub_raw = form.get("sub_lines", "")
        sub_pairs = _parse_sub_lines(sub_raw)

    payload = {
        "id": form.get("id", "").strip(),
        "main": {"group_id": main_group_id, "num": main_num},
        "sub": sub_pairs,
        "date": form["date"].strip(),
        "holding": form["holding"].strip(),
        "start_time": form.get("start_time") or None,
        "end_time": form.get("end_time") or None,
        "agenda": _parse_agenda(agenda_raw),
        "attendee": attendees,
        "sources": _parse_sources(sources_raw),
        "materials": _parse_materials(materials_raw),
    }
    return payload


@app.post("/meeting/new")
def meeting_create() -> str:
    groups = load_groups()
    persons = load_persons()
    try:
        payload = _extract_meeting_form(request.form)
        meeting_id = str(uuid4())
        payload["id"] = meeting_id
        save_meeting(meeting_id, payload)
        return redirect(url_for("meeting_detail", id=meeting_id))
    except Exception as e:  # noqa: BLE001
        return render_template(
            "meeting_form.html",
            meeting=request.form,
            mode="new",
            groups=groups,
            persons=persons,
            error=str(e),
        )


@app.get("/meeting/<id>")
def meeting_detail(id: str) -> str:
    path = data_dir() / "meeting" / id / "basic.json"
    if not path.exists():
        return "not found", 404
    meeting = _load_json(path, {})
    meeting["id"] = id
    groups = load_groups()
    persons = load_persons()
    group_map = {g["id"]: g["name"] for g in groups}
    person_map = {p["id"]: p["name"] for p in persons}
    return render_template(
        "meeting_detail.html",
        meeting=meeting,
        group_map=group_map,
        person_map=person_map,
    )


@app.get("/meeting/<id>/edit")
def meeting_edit(id: str) -> str:
    path = data_dir() / "meeting" / id / "basic.json"
    if not path.exists():
        return "not found", 404
    meeting = _load_json(path, {})
    meeting["id"] = id
    groups = load_groups()
    persons = load_persons()
    # populate helper fields
    sub_list = meeting.get("sub", [])
    meeting["sub_group_id_list"] = [s["group_id"] for s in sub_list] + ["" for _ in range(3 - len(sub_list))]
    meeting["sub_num_list"] = [s["num"] for s in sub_list] + ["" for _ in range(3 - len(sub_list))]
    meeting["attendee_multi"] = meeting.get("attendee", [])
    meeting["agenda_lines"] = "\n".join(meeting.get("agenda", []))
    meeting["sources_lines"] = "\n".join(
        f"{s.get('url','')}|{s.get('source_type','')}|{s.get('title','') or ''}"
        for s in meeting.get("sources", [])
    )
    meeting["materials_lines"] = "\n".join(
        f"{m.get('url','')}|{m.get('title','') or ''}" for m in meeting.get("materials", [])
    )
    return render_template(
        "meeting_form.html",
        meeting=meeting,
        mode="edit",
        groups=groups,
        persons=persons,
        error=None,
    )


@app.post("/meeting/<id>/edit")
def meeting_update(id: str) -> str:
    groups = load_groups()
    persons = load_persons()
    try:
        payload = _extract_meeting_form(request.form)
        payload["id"] = id
        save_meeting(id, payload)
        return redirect(url_for("meeting_detail", id=id))
    except Exception as e:  # noqa: BLE001
        return render_template(
            "meeting_form.html",
            meeting=request.form,
            mode="edit",
            groups=groups,
            persons=persons,
            error=str(e),
        )


@app.post("/meeting/<id>/delete")
def meeting_delete(id: str) -> str:
    delete_meeting(id)
    return redirect(url_for("meeting_list"))


def _find_meetings_with_person(person_id: str) -> List[Dict[str, Any]]:
    meetings = load_meetings()
    return [m for m in meetings if person_id in m.get("attendee", [])]


@app.post("/person/<id>/delete")
def person_delete(id: str) -> str:
    linked_meetings = _find_meetings_with_person(id)
    if linked_meetings and request.form.get("confirm") != "yes":
        # 確認ページへ
        group_map = {g["id"]: g["name"] for g in load_groups()}
        return render_template(
            "person_delete_confirm.html",
            person_id=id,
            meetings=linked_meetings,
            group_map=group_map,
        )

    # remove_attendance が on の場合は該当会議からattendeeを外す
    if request.form.get("remove_attendance") == "on":
        for m in _find_meetings_with_person(id):
            m["attendee"] = [a for a in m.get("attendee", []) if a != id]
            save_meeting(m["id"], m)

    delete_person(id)
    return redirect(url_for("person_list"))


if __name__ == "__main__":
    app.run(debug=True, port=8000)

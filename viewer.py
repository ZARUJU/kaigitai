from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Flask, abort, render_template, request, url_for as flask_url_for

from src.utils import data_dir

DISCLAIMER_TEXT = "本サイトの掲載情報は正確性を保証しません。参考情報としてご利用ください。"
# GitHub Pagesのプロジェクトページ配下で動かすためのベースパス
BASE_PATH = "/kaigitai"

app = Flask(__name__)


def _prefixed_url_for(endpoint: str, **values: Any) -> str:
    """url_for結果にベースパスを付与する（外部URLは除外）。"""
    url = flask_url_for(endpoint, **values)
    if url.startswith("http://") or url.startswith("https://"):
        return url
    prefix = BASE_PATH.rstrip("/")
    return f"{prefix}{url}"


# ===== helpers =====


def _load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


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

    def sort_key(m: Dict[str, Any]) -> Any:
        return (m.get("date") or "", m.get("main", {}).get("num") or 0)

    return sorted(results, key=sort_key, reverse=True)


def _clean_url(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    v = value.strip()
    return v or None


def normalize_sources(raw: Any) -> Dict[str, Any]:
    if not raw:
        return {"meeting_page": None, "transcript": None, "announcement": None, "other": []}
    if isinstance(raw, dict):
        return {
            "meeting_page": _clean_url(raw.get("meeting_page")),
            "transcript": _clean_url(raw.get("transcript")),
            "announcement": _clean_url(raw.get("announcement") or raw.get("notice")),
            "other": raw.get("other") or [],
        }
    meeting_page = None
    transcript = None
    announcement = None
    other_items: List[Dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        url = _clean_url(item.get("url"))
        if not url:
            continue
        stype = item.get("source_type")
        title = item.get("title")
        if stype == "meeting_page" and not meeting_page:
            meeting_page = url
        elif stype in ("minutes", "transcript") and not transcript:
            transcript = url
        elif stype in ("announcement", "notice") and not announcement:
            announcement = url
        else:
            other_items.append({"url": url, "title": title})
    return {
        "meeting_page": meeting_page,
        "transcript": transcript,
        "announcement": announcement,
        "other": other_items,
    }


def build_group_tree(level_limit: Optional[int] = None) -> tuple[List[Dict[str, Any]], int]:
    groups = load_groups()
    by_parent: Dict[Optional[str], List[Dict[str, Any]]] = {}
    for g in groups:
        by_parent.setdefault(g.get("parent"), []).append(g)

    def build(parent_id: Optional[str], depth: int) -> List[Dict[str, Any]]:
        nodes: List[Dict[str, Any]] = []
        for child in by_parent.get(parent_id, []):
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


@app.context_processor
def inject_globals() -> Dict[str, Any]:
    return {
        "readonly": True,
        "site_title": "kaigitai viewer",
        "site_subtitle": "閲覧専用",
        "disclaimer_text": DISCLAIMER_TEXT,
    }


# viewer用にurl_forを差し替え
app.jinja_env.globals["url_for"] = _prefixed_url_for


# ===== routes =====


@app.get("/")
def index() -> str:
    return render_template("viewer_index.html")


@app.get("/group/")
def group_list() -> str:
    groups = load_groups()
    return render_template("group_list.html", groups=groups)


@app.get("/group/<id>/")
def group_detail(id: str) -> str:
    path = data_dir() / "group" / f"{id}.json"
    if not path.exists():
        abort(404)
    group = _load_json(path, {})
    group["id"] = id
    groups = load_groups()
    group_map = {g["id"]: g["name"] for g in groups}
    group_name_map = {g["name"]: g["id"] for g in groups}
    parent_label = "-"
    parent_id_for_link = None
    if group.get("parent"):
        parent_id = group["parent"]
        parent_name = next((g["name"] for g in groups if g.get("id") == parent_id), None)
        if not parent_name:
            # 親がnameで保存されている場合に解決を試みる
            resolved = group_name_map.get(parent_id)
            if resolved:
                parent_id = resolved
                parent_name = group_map.get(parent_id)
        parent_label = f"{parent_name} ({parent_id})" if parent_name else parent_id
        parent_id_for_link = parent_id if parent_name else None
    meetings = load_meetings()
    main_meetings = [m for m in meetings if m.get("main", {}).get("group_id") == id]
    sub_meetings = [m for m in meetings if any(sub.get("group_id") == id for sub in m.get("sub", []))]
    return render_template(
        "group_detail.html",
        group=group,
        parent_label=parent_label,
        parent_id=parent_id_for_link,
        main_meetings=main_meetings,
        sub_meetings=sub_meetings,
        group_map=group_map,
    )


@app.get("/group/tree/")
def group_tree() -> str:
    tree, max_level = build_group_tree()
    return render_template("group_tree.html", tree=tree, level=None, max_level=max_level)


@app.get("/group/tree/<int:level>/")
def group_tree_level(level: int) -> str:
    level_limit = level if level > 0 else None
    tree, max_level = build_group_tree(level_limit)
    return render_template("group_tree.html", tree=tree, level=level_limit, max_level=max_level)


@app.get("/group/<id>/children/")
def group_children(id: str) -> str:
    groups = load_groups()
    current = next((g for g in groups if g.get("id") == id), None)
    if current is None:
        abort(404)
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


@app.get("/person/")
def person_list() -> str:
    persons = load_persons()
    return render_template("person_list.html", persons=persons)


@app.get("/person/<id>/")
def person_detail(id: str) -> str:
    path = data_dir() / "person" / f"{id}.json"
    if not path.exists():
        abort(404)
    person = _load_json(path, {})
    person["id"] = id
    return render_template("person_detail.html", person=person)


@app.get("/meeting/")
def meeting_list() -> str:
    q = request.args.get("q", "").strip().lower()
    meetings = load_meetings()
    if q:
        meetings = [
            m
            for m in meetings
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


@app.get("/meeting/<id>/")
def meeting_detail(id: str) -> str:
    path = data_dir() / "meeting" / id / "basic.json"
    if not path.exists():
        abort(404)
    meeting = _load_json(path, {})
    meeting["id"] = id
    meeting["sources"] = normalize_sources(meeting.get("sources"))
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


if __name__ == "__main__":
    app.run(debug=True, port=9000)

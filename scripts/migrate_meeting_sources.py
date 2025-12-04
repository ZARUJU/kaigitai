from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def data_dir() -> Path:
    return repo_root() / "data" / "meeting"


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


def migrate_one(path: Path) -> bool:
    payload = json.loads(path.read_text(encoding="utf-8"))
    before = payload.get("sources")
    after = normalize_sources(before)
    if before == after:
        return False
    payload["sources"] = after
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def main() -> None:
    base = data_dir()
    if not base.exists():
        print("meeting data dir not found; nothing to do")
        return
    changed = 0
    for folder in sorted(p for p in base.iterdir() if p.is_dir()):
        target = folder / "basic.json"
        if not target.exists():
            continue
        if migrate_one(target):
            changed += 1
            print(f"[migrated] {target}")
    print(f"done. updated: {changed}")


if __name__ == "__main__":
    main()

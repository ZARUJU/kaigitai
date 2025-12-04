from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask_frozen import Freezer
from viewer import app, build_group_tree, load_groups, load_meetings, load_persons

app.config["FREEZER_DESTINATION"] = str(ROOT / "build")

freezer = Freezer(app)


@freezer.register_generator
def group_detail() -> str:
    for g in load_groups():
        yield "group_detail", {"id": g["id"]}


@freezer.register_generator
def person_detail() -> str:
    for p in load_persons():
        yield "person_detail", {"id": p["id"]}


@freezer.register_generator
def meeting_detail() -> str:
    for m in load_meetings():
        yield "meeting_detail", {"id": m["id"]}


@freezer.register_generator
def group_tree_level() -> str:
    _, max_depth = build_group_tree()
    for lv in range(1, max_depth + 1):
        yield "group_tree_level", {"level": lv}


@freezer.register_generator
def group_children() -> str:
    for g in load_groups():
        yield "group_children", {"id": g["id"]}


if __name__ == "__main__":
    freezer.freeze()

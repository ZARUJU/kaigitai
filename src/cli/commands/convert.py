from __future__ import annotations

from src.core.convert import convert_group, convert_meeting, convert_person


def run_convert() -> None:
    dry = input("dry-runで実行しますか？ (y/N): ").strip().lower() == "y"
    strict = input("未登録nameはエラーにしますか？ (Y/n): ").strip().lower() != "n"

    print("[convert] group を処理します")
    group_registry, group_result = convert_group(dry_run=dry)
    print(f"  created: {group_result.created}, updated: {group_result.updated}")

    print("[convert] person を処理します")
    person_registry, person_result = convert_person(dry_run=dry)
    print(f"  created: {person_result.created}, updated: {person_result.updated}")

    print("[convert] meeting を処理します")
    meeting_result = convert_meeting(group_registry, person_registry, dry_run=dry, strict_missing=strict)
    print(f"  created: {meeting_result.created}, updated: {meeting_result.updated}, skipped: {meeting_result.skipped}")
    if meeting_result.errors:
        print("  errors:")
        for err in meeting_result.errors:
            print(f"    - {err}")

    if dry:
        print("dry-runのためファイルは書き込みません。予定出力:")
        for p in group_result.planned + person_result.planned + meeting_result.planned:
            print(f"  - {p}")
    else:
        print("変換完了")

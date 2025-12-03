from __future__ import annotations

from typing import Callable, Dict

from src.cli.commands.convert import run_convert
from src.cli.commands.fragment import run_fragment
from src.cli.commands.validate import run_validate

MenuAction = Callable[[], None]


def run_menu() -> None:
    menu: Dict[str, MenuAction] = {
        "1": run_convert,
        "2": run_validate,
        "3": run_fragment,
    }
    print("1) register→data 変換")
    print("2) スキーマ検証のみ")
    print("3) fragment生成")
    choice = input("選択肢を入力してください (1-3): ").strip()
    action = menu.get(choice)
    if action is None:
        print("無効な選択です。1-3から選んでください。")
        return
    action()

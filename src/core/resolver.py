from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
from uuid import uuid4


@dataclass
class NameRegistry:
    name_to_id: Dict[str, str]

    @classmethod
    def from_lists(cls, pairs: List[Dict[str, str]]) -> "NameRegistry":
        mapping: Dict[str, str] = {}
        for item in pairs:
            name = item["name"]
            value_id = item["id"]
            key = cls._normalize(name)
            mapping[key] = value_id
            # UUIDが直接指定された場合も解決できるよう、ID自体もキーに登録する
            mapping[cls._normalize(value_id)] = value_id
        return cls(mapping)

    @staticmethod
    def _normalize(name: str) -> str:
        return name.strip()

    def resolve(self, name: str) -> str:
        key = self._normalize(name)
        if key not in self.name_to_id:
            raise ValueError(f"未登録の名前です: {name}")
        return self.name_to_id[key]

    def resolve_or_create(self, name: str) -> str:
        key = self._normalize(name)
        found = self.name_to_id.get(key)
        if found:
            return found
        new_id = str(uuid4())
        self.name_to_id[key] = new_id
        return new_id

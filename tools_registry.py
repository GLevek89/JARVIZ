from __future__ import annotations

from dataclasses import dataclass
from typing import List

@dataclass
class ToolAction:
    id: str
    title: str
    keywords: List[str]
    open_page_id: str

class ToolRegistry:
    def __init__(self) -> None:
        self._actions: List[ToolAction] = []

    def register(self, action: ToolAction) -> None:
        self._actions.append(action)

    def search(self, query: str) -> List[ToolAction]:
        q = (query or "").strip().lower()
        if not q:
            return []
        def score(a: ToolAction) -> int:
            hay = " ".join([a.title] + a.keywords).lower()
            if q in hay:
                return 100
            parts = q.split()
            return sum(10 for p in parts if p in hay)
        ranked = [(score(a), a) for a in self._actions]
        ranked = [x for x in ranked if x[0] > 0]
        ranked.sort(key=lambda x: x[0], reverse=True)
        return [a for _, a in ranked]

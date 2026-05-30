"""The device-agnostic contract.

Raspberry Pi / TTS layer ever sees. knows
nothing about HTML, the DOM, or how the tree was fetched. 
"""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class A11yItem:
    id: int                       # stable index within this page snapshot
    role: str                     # heading | link | button | textbox | ...
    name: str                     # the accessible label (what TTS speaks)
    landmark: Optional[str] = None  # which page region it lives in (main/nav/footer/...)
    level: Optional[int] = None     # heading level (1-6), else None
    importance: float = 0.0         # heuristic 0..1 score (LLM can overwrite later)

    def to_dict(self):
        return asdict(self)

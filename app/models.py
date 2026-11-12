"""S2: the Record dataclass used across the project."""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Record:
    topic: str
    place_or_service: str
    timing: str
    cost_inr: Optional[int]
    rule_or_tip: str
    source_url: str
    checked_on: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
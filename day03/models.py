"""Record dataclass for ShirdiYatra data."""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Record:
    topic: str
    place_or_service: str
    timing: Optional[str]
    cost_inr: Optional[int]
    rule_or_tip: Optional[str]
    source_url: str
    checked_on: str = ""

    def __post_init__(self):
        if not self.topic or not self.topic.strip():
            raise ValueError("topic is empty")
        if not self.place_or_service or not self.place_or_service.strip():
            raise ValueError("place_or_service is empty")
        if not self.source_url.startswith("https://sai.org.in/"):
            raise ValueError(f"not an official source: {self.source_url}")
        if self.cost_inr is not None and self.cost_inr < 0:
            raise ValueError("cost_inr cannot be negative")

    def to_dict(self) -> dict:
        return asdict(self)
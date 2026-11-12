"""app/models.py - the Record data model for ShirdiYatra (Day 3)."""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Record:
    topic: str                      # "Daily programme", "Accommodation", "Travel", ...
    place_or_service: str           # e.g. "Kakad Aarti (Morning)" or "Sai Bhakta Niwas - ..."
    timing: str                     # e.g. "5:15 AM" or "Per day, stay 24-48 hours"
    cost_inr: Optional[int]         # None when the page lists no amount, 0 if free
    rule_or_tip: str
    source_url: str                 # official domain only (sai.org.in)
    checked_on: str                 # date the page was downloaded, e.g. "2026-11-12"

    def to_dict(self):
        return asdict(self)

    def short(self):
        if self.cost_inr is None:
            cost = "-"
        elif self.cost_inr == 0:
            cost = "Free"
        else:
            cost = f"Rs {self.cost_inr}"
        return f"{self.topic} | {self.place_or_service} | {self.timing} | {cost}"


if __name__ == "__main__":
    r = Record("Daily programme", "Kakad Aarti (Morning)", "5:15 AM", None,
               "One of the four main aartis", "https://sai.org.in/en/daily-programme",
               "2026-11-12")
    print(r.short())

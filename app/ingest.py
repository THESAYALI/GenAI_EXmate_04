"""S1: clean data/raw/*.html into data/records.json."""
import json
import re
import sys
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup

try:
    from app.models import Record      # python -m app.ingest
except ImportError:
    from models import Record          # python app\ingest.py

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUT_FILE = BASE_DIR / "data" / "records.json"

DAILY_URL = "https://sai.org.in/en/daily-programme"
ROOMS_URL = "https://sai.org.in/en/accomodations"
STAY_RULE = "Rooms are allotted for a minimum of 24 and maximum of 48 hours"


def to_int(text: str):
    m = re.search(r"\d+", text.replace(",", ""))
    return int(m.group()) if m else None


def parse_daily(html: str, url: str, checked_on: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    records = []
    for li in soup.find_all("li"):
        if not li.find("img", src=re.compile(r"clock-")) or li.find("li"):
            continue
        try:
            lines = [t for t in li.get_text("\n", strip=True).split("\n") if t]
            if len(lines) < 2:
                raise ValueError("no time found")
            title, timing = lines[0], lines[-1]
            records.append(Record(
                topic="daily programme",
                place_or_service=title,
                timing=timing,
                cost_inr=None,
                rule_or_tip="Timings can change on festival days; confirm on the Sansthan site.",
                source_url=url,
                checked_on=checked_on,
            ))
        except Exception as e:
            print(f"  skipped bad daily row: {e}")
    return records


def parse_rooms(html: str, url: str, checked_on: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    records, seen = [], set()
    keys = ("location", "room type", "description", "min", "max", "rate", "remark")

    for table in soup.find_all("table"):
        headers = [c.get_text(" ", strip=True).lower() for c in table.find_all("th")]
        if not any("rate" in h for h in headers):
            continue
        idx = {}
        for i, h in enumerate(headers):
            for k in keys:
                if k in h and k not in idx:
                    idx[k] = i
        if not {"location", "room type", "rate"} <= idx.keys():
            continue

        for tr in table.find_all("tr"):
            try:
                tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
                if len(tds) <= max(idx.values()):
                    continue
                cost = to_int(tds[idx["rate"]])
                if cost is None:
                    continue  # no published tariff, cannot be planned
                raw_loc = tds[idx["location"]]
                dist = re.search(r"\(([^)]*)\)", raw_loc)
                loc = re.sub(r"\s*\(.*?\)", "", raw_loc).strip()
                place = f"{loc} - {tds[idx['room type']]}"
                lo = tds[idx["min"]] if "min" in idx else "?"
                hi = tds[idx["max"]] if "max" in idx else "?"
                desc = tds[idx["description"]] if "description" in idx else ""
                remark = tds[idx["remark"]] if "remark" in idx else ""
                tip = f"Capacity {lo}-{hi}. {desc}. {remark}".replace(". .", ".").strip(" .") + "."
                if dist:
                    tip += f" {dist.group(1).strip()}."
                norm = re.sub(r"[^a-z]", "", loc.lower()).replace("bhaktiniwas", "bhaktniwas")
                key = (norm, lo, hi, cost)
                if key in seen:
                    continue
                seen.add(key)
                records.append(Record(
                    topic="accommodation",
                    place_or_service=place,
                    timing=STAY_RULE,
                    cost_inr=cost,
                    rule_or_tip=tip,
                    source_url=url,
                    checked_on=checked_on,
                ))
            except Exception as e:
                print(f"  skipped bad room row: {e}")
    return records

def read_raw(name: str):
    path = RAW_DIR / f"{name}.html"
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"  cannot read {path.name}: {e}")
        return None


def main() -> int:
    checked_on = date.today().isoformat()
    try:
        manifest = json.loads((RAW_DIR / "manifest.json").read_text(encoding="utf-8"))
        checked_on = manifest["daily_programme"].get("fetched_on", checked_on)
    except (OSError, KeyError, ValueError):
        pass

    records = []
    daily = read_raw("daily_programme")
    if daily:
        found = parse_daily(daily, DAILY_URL, checked_on)
        print(f"daily programme: {len(found)} records")
        records += found
    rooms = read_raw("accommodations")
    if rooms:
        found = parse_rooms(rooms, ROOMS_URL, checked_on)
        print(f"accommodation: {len(found)} records")
        records += found

    if not records:
        print("No records produced.")
        return 1
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(
        json.dumps([r.to_dict() for r in records], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Saved {len(records)} records to {OUT_FILE.relative_to(BASE_DIR)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
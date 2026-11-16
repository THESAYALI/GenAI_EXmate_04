"""Day 09 / S1 - agent tool: plan_sansthan_rooms (pure Python, no libraries).

Rules implemented
  * Tariff comes from data/room_tariff.csv (min/max capacity, rate, extra person charge).
  * A room's rate covers `min_capacity` people. Each person above that (up to
    `max_capacity`) costs `extra_person_charge` per night.
  * No single-person rooms: every room must hold at least 2 people.
  * Stay must be 24-48 hours -> nights is 1 or 2 (stay_hours = nights * 24).
  * Result = the CHEAPEST mix of rooms for the whole group (dynamic programming).
"""
import csv
from collections import Counter
from pathlib import Path

TARIFF_PATH = Path(__file__).resolve().parent.parent / "data" / "room_tariff.csv"
MIN_PEOPLE_PER_ROOM = 2          # rule: no single-person rooms
ALLOWED_NIGHTS = (1, 2)          # rule: 24-48 hour stay


def _to_bool(value):
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower().replace("-", "").replace(" ", "")
    if text in ("true", "yes", "1", "ac"):
        return True
    if text in ("false", "no", "0", "nonac"):
        return False
    raise ValueError(f"cannot understand AC value: {value!r}")


def load_tariff(path=None):
    """Read the tariff CSV into a list of dicts with proper types."""
    rooms = []
    with open(path or TARIFF_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rooms.append({
                "room_type": row["room_type"].strip(),
                "ac": _to_bool(row["ac"]),
                "min_capacity": int(row["min_capacity"]),
                "max_capacity": int(row["max_capacity"]),
                "rate_per_night": float(row["rate_per_night"]),
                "extra_person_charge": float(row["extra_person_charge"]),
            })
    return rooms


def room_cost(room, occupants, nights):
    """Cost of ONE room with `occupants` people for `nights` nights."""
    extra = max(0, occupants - room["min_capacity"])
    return (room["rate_per_night"] + extra * room["extra_person_charge"]) * nights


def plan_sansthan_rooms(group_size, ac, nights, tariff_path=None):
    """Return the cheapest room mix. Always returns a dict; check result['ok']."""
    try:
        group_size, nights, ac = int(group_size), int(nights), _to_bool(ac)
    except (TypeError, ValueError) as e:
        return {"ok": False, "error": f"bad input: {e}"}

    if group_size < MIN_PEOPLE_PER_ROOM:
        return {"ok": False, "error": "No single-person rooms: a group needs at least 2 people."}
    if nights not in ALLOWED_NIGHTS:
        return {"ok": False, "error": "Stay must be 24-48 hours, so nights must be 1 or 2."}

    options = [r for r in load_tariff(tariff_path) if r["ac"] == ac]
    if not options:
        return {"ok": False, "error": "No rooms of that type in the tariff."}

    # best[n] = (cost, [(room, occupants), ...]) for housing exactly n people
    best = [None] * (group_size + 1)
    best[0] = (0.0, [])
    for n in range(1, group_size + 1):
        for room in options:
            lo = max(room["min_capacity"], MIN_PEOPLE_PER_ROOM)
            for k in range(lo, room["max_capacity"] + 1):
                if k > n or best[n - k] is None:
                    continue
                cost = best[n - k][0] + room_cost(room, k, nights)
                rooms_used = len(best[n - k][1]) + 1
                cur = best[n]
                if cur is None or cost < cur[0] or (cost == cur[0] and rooms_used < len(cur[1])):
                    best[n] = (cost, best[n - k][1] + [(room, k)])

    if best[group_size] is None:
        return {"ok": False,
                "error": f"Cannot house exactly {group_size} people without a single-person room."}

    total, chosen = best[group_size]
    counts = Counter((r["room_type"], k) for r, k in chosen)
    by_name = {r["room_type"]: r for r in options}
    rooms = [{
        "room_type": name, "count": cnt, "occupants_per_room": k,
        "cost_per_room": room_cost(by_name[name], k, nights),
        "subtotal": room_cost(by_name[name], k, nights) * cnt,
    } for (name, k), cnt in sorted(counts.items())]

    return {"ok": True, "group_size": group_size, "ac": ac, "nights": nights,
            "stay_hours": nights * 24, "rooms": rooms, "total_cost": total}


if __name__ == "__main__":      # interactive: python -m app.tools
    size = int(input("Group size: "))
    is_ac = input("AC? (y/n): ").strip().lower().startswith("y")
    n = int(input("Nights (1 or 2): "))
    print(plan_sansthan_rooms(size, is_ac, n))

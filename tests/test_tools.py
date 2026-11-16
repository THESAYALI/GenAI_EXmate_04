from app.tools import plan_sansthan_rooms


def test_family_of_7_ac():
    r = plan_sansthan_rooms(7, True, 2)
    assert r["ok"] and r["stay_hours"] == 48
    assert sum(x["count"] * x["occupants_per_room"] for x in r["rooms"]) == 7
    assert all(x["occupants_per_room"] >= 2 for x in r["rooms"])


def test_no_single_person():
    assert not plan_sansthan_rooms(1, False, 1)["ok"]


def test_nights_rule():
    assert not plan_sansthan_rooms(4, False, 3)["ok"]
    assert not plan_sansthan_rooms(4, False, 0)["ok"]


def test_cheapest_beats_naive():
    r = plan_sansthan_rooms(6, False, 1)
    assert r["ok"] and r["total_cost"] <= 700

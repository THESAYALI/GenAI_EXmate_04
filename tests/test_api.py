import pytest


def _items(data):
    """Return the list of records whether the API returns a list or a wrapper dict."""
    if isinstance(data, list):
        return data
    for key in ("records", "items", "results", "data"):
        if isinstance(data.get(key), list):
            return data[key]
    return []


def test_list_records(client):
    resp = client.get("/records")
    assert resp.status_code == 200
    assert len(_items(resp.json())) > 0


def test_get_record_by_id(client):
    items = _items(client.get("/records").json())
    record_id = items[0].get("id")
    if record_id is None:
        pytest.skip("records have no id field")
    resp = client.get(f"/records/{record_id}")
    assert resp.status_code == 200


def test_get_record_not_found(client):
    resp = client.get("/records/999999")
    assert resp.status_code == 404
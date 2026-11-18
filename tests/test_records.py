def test_list_records_returns_all(client):
    data = client.get("/api/records").get_json()
    assert data["count"] == len(data["records"]) >= 10


def test_list_records_filters_by_category(client):
    data = client.get("/api/records?category=nearby").get_json()
    assert data["count"] >= 2
    assert all(r["category"] == "nearby" for r in data["records"])


def test_list_records_respects_limit(client):
    data = client.get("/api/records?limit=3").get_json()
    assert data["count"] == 3


def test_get_record_by_id(client):
    resp = client.get("/api/records/1")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Sai Baba Samadhi Mandir"


def test_get_record_not_found(client):
    resp = client.get("/api/records/9999")
    assert resp.status_code == 404
    assert "error" in resp.get_json()

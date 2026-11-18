from app.records import load_records
from app.search import search, tokenize


def test_search_finds_by_name(client):
    data = client.get("/api/search?q=dwarkamai").get_json()
    assert data["count"] >= 1
    assert data["results"][0]["name"] == "Dwarkamai"


def test_search_finds_by_tag(client):
    data = client.get("/api/search?q=jyotirlinga").get_json()
    assert any("Trimbakeshwar" in r["name"] for r in data["results"])


def test_search_requires_query(client):
    resp = client.get("/api/search?q=")
    assert resp.status_code == 400


def test_search_no_match_returns_empty(client):
    data = client.get("/api/search?q=zzzzqqqq").get_json()
    assert data["count"] == 0
    assert data["results"] == []


def test_search_ranks_name_match_first():
    results = search(load_records(), "museum")
    assert results[0]["name"] == "Shirdi Sai Baba Museum"


def test_tokenize_drops_stopwords_and_case():
    assert tokenize("What is the Aarti TIME") == ["aarti", "time"]

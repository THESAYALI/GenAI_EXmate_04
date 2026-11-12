"""app/smart_search.py - rank records with TF-IDF + cosine similarity (Day 4).

Powers the /search endpoint in app/main.py. Try it without the API:
    python -m app.smart_search shej aarti
"""
import sys

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app import records as db

TEXT_FIELDS = ("topic", "place_or_service", "timing", "rule_or_tip")


def record_text(record):
    return " ".join(str(record.get(f, "")) for f in TEXT_FIELDS)


class SmartSearch:
    def __init__(self, records):
        self.records = records
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform([record_text(r) for r in records])

    def search(self, query, top_k=5):
        """Best-matching records, highest score first. Records with score 0 are left out."""
        if not query or not query.strip() or not self.records:
            return []
        scores = cosine_similarity(self.vectorizer.transform([query]), self.matrix).ravel()
        ranked = scores.argsort()[::-1][:top_k]
        return [{**self.records[i], "score": round(float(scores[i]), 4)}
                for i in ranked if scores[i] > 0]


def load_default():
    """Records with ids, from data/records.json if it exists, else data/sample_records.json."""
    return db.with_ids(db.load_records(db.default_data_file()))


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "family room"
    for hit in SmartSearch(load_default()).search(query):
        print(f"{hit['score']:.3f}  #{hit['id']}  {hit['place_or_service']}  ({hit['timing']})")

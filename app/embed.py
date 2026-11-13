"""
app/embed.py  --  D7 / S1
Turns text into vectors (embeddings) so we can search by MEANING, not just keywords.
Model: sentence-transformers 'all-MiniLM-L6-v2' (free, runs on your laptop, 384 numbers per text).
First run downloads ~90 MB once; after that it works offline.
"""
import os

MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer  # imported lazily: slow import
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts, batch_size=32):
    """list[str] -> list[list[float]] (normalised, so cosine similarity = dot product)."""
    vectors = _get_model().encode(
        list(texts), batch_size=batch_size, normalize_embeddings=True, show_progress_bar=False
    )
    return vectors.tolist()


def embed_query(text):
    return embed_texts([text])[0]


if __name__ == "__main__":
    v = embed_query("What time is the Kakad aarti?")
    print(f"model={MODEL_NAME}  dimensions={len(v)}  first 5 numbers={[round(x, 3) for x in v[:5]]}")

"""
app/vectorstore.py  --  D7 / S2
Persistent Chroma collection holding every chunk + its embedding.
Stored on disk in data/chroma/, so you build it once and reuse it after restarts.
"""
from pathlib import Path

import chromadb

from app.chunking import load_all_chunks
from app.embed import embed_query, embed_texts

ROOT = Path(__file__).resolve().parent.parent
CHROMA_DIR = ROOT / "data" / "chroma"
COLLECTION = "shirdiyatra"


def _client():
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_collection():
    return _client().get_or_create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})


def count():
    return get_collection().count()


def build_index(reset=True):
    """Chunk all documents, embed them and store them. Returns number of chunks indexed."""
    chunks = load_all_chunks()
    if not chunks:
        raise RuntimeError("No chunks found. Put data in data/records.json or data/raw/ first.")
    client = _client()
    if reset:
        try:
            client.delete_collection(COLLECTION)
        except Exception:
            pass
    col = client.get_or_create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})
    for start in range(0, len(chunks), 100):
        batch = chunks[start:start + 100]
        col.add(
            ids=[c["id"] for c in batch],
            documents=[c["text"] for c in batch],
            embeddings=embed_texts([c["text"] for c in batch]),
            metadatas=[{"source": c["source"], "page": c["page"],
                        "title": c["title"], "chunk_index": c["chunk_index"]} for c in batch],
        )
    return len(chunks)


def semantic_search(query, k=5):
    """Return the k chunks closest in meaning to the query."""
    col = get_collection()
    if col.count() == 0:
        build_index()
        col = get_collection()
    res = col.query(query_embeddings=[embed_query(query)], n_results=k,
                    include=["documents", "metadatas", "distances"])
    hits = []
    for i in range(len(res["ids"][0])):
        meta = res["metadatas"][0][i]
        hits.append({
            "id": res["ids"][0][i],
            "score": round(1 - res["distances"][0][i], 4),  # cosine similarity, higher = better
            "title": meta["title"],
            "source": meta["source"],
            "page": meta["page"],
            "text": res["documents"][0][i],
        })
    return hits


if __name__ == "__main__":
    n = build_index()
    print(f"Indexed {n} chunks into {CHROMA_DIR}  (collection total: {count()})")

"""
app/semantic_routes.py  --  D7 / S2
GET  /search/semantic?q=...&k=5   -> semantic (meaning-based) search
POST /search/reindex              -> rebuild the Chroma collection

Add to app/main.py (2 lines):
    from app.semantic_routes import router as semantic_router
    app.include_router(semantic_router)
"""
from fastapi import APIRouter, HTTPException, Query

from app import vectorstore

router = APIRouter(tags=["semantic search"])


@router.get("/search/semantic")
def search_semantic(q: str = Query(..., min_length=2, description="Your question"),
                    k: int = Query(5, ge=1, le=20)):
    try:
        hits = vectorstore.semantic_search(q, k=k)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"query": q, "count": len(hits), "results": hits}


@router.post("/search/reindex")
def reindex():
    try:
        return {"indexed_chunks": vectorstore.build_index()}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

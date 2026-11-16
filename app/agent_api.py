"""Day 09 / S2 - POST /agent. Add to app/main.py:

    from app.agent_api import router as agent_router
    app.include_router(agent_router)
"""
from typing import Optional

from fastapi import APIRouter
from langgraph.types import Command
from pydantic import BaseModel

from app.graph import graph

router = APIRouter()


class AgentIn(BaseModel):
    message: Optional[str] = None      # a new user message ...
    approve: Optional[bool] = None     # ... or the answer to a pending approval
    thread_id: str = "default"         # one memory per thread_id


@router.post("/agent")
def agent(req: AgentIn):
    config = {"configurable": {"thread_id": req.thread_id}}
    if req.approve is not None:
        result = graph.invoke(Command(resume=req.approve), config)
    else:
        result = graph.invoke({"user_input": req.message or ""}, config)

    if result.get("__interrupt__"):
        return {"status": "awaiting_approval", "thread_id": req.thread_id,
                "proposal": result["__interrupt__"][0].value}
    return {"status": "done", "thread_id": req.thread_id, "answer": result.get("answer"),
            "remembered": {k: result.get(k) for k in ("group_size", "ac", "nights")}}

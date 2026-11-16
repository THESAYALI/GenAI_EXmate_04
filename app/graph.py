"""Day 09 / S2 - the same agent rebuilt in LangGraph, with memory + ONE approval step.

  understand -> rag -> (rooms -> approval) -> answer

* Memory: MemorySaver checkpointer, keyed by thread_id. group_size / ac / nights
  stay in state, so "make it 2 nights" works on the next turn.
* Approval: the `approval` node calls interrupt(); the graph pauses until the
  caller resumes it with Command(resume=True/False).
"""
from typing import Annotated, Optional, TypedDict
import operator

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from app.agent_loop import call_llm, extract_trip_params, format_answer, search_docs, wants_rooms
from app.tools import plan_sansthan_rooms


class State(TypedDict, total=False):
    user_input: str
    messages: Annotated[list, operator.add]     # chat history (memory)
    group_size: int
    ac: bool
    nights: int
    docs: list
    plan: Optional[dict]
    approved: Optional[bool]
    answer: str


def understand(state: State):
    text = state["user_input"]
    update = {"messages": [{"role": "user", "content": text}], "plan": None, "approved": None}
    update.update(extract_trip_params(text))     # new values override remembered ones
    return update


def rag(state: State):
    return {"docs": search_docs(state["user_input"])}


def route_after_rag(state: State):
    ready = all(state.get(k) is not None for k in ("group_size", "ac", "nights"))
    return "rooms" if wants_rooms(state["user_input"]) and ready else "answer"


def rooms(state: State):
    return {"plan": plan_sansthan_rooms(state["group_size"], state["ac"], state["nights"])}


def approval(state: State):
    plan = state["plan"]
    if not plan.get("ok"):
        return {"approved": False}
    decision = interrupt({"question": "Approve this room plan?", "plan": plan})
    return {"approved": bool(decision)}


def route_after_rooms(state: State):
    return "approval" if state["plan"].get("ok") else "answer"


def answer(state: State):
    plan, docs = state.get("plan"), state.get("docs", [])
    if plan is not None:
        if not plan.get("ok"):
            text = "I could not plan rooms: " + plan["error"]
        elif state.get("approved"):
            text = "Approved. " + format_answer("", [{"tool": "plan_sansthan_rooms", "result": plan}])
        else:
            text = "Okay, I will not finalise that plan. Tell me what to change (group size, AC/non-AC, nights)."
    else:
        text = None
        context = "\n".join(d["text"] for d in docs)
        text = call_llm(f"Answer ONLY from this context, else say \"I don't know\".\nContext:\n{context}\n\nQuestion: {state['user_input']}")
        if not text:
            text = format_answer(state["user_input"], [{"tool": "search_docs", "result": docs}])
        missing = [k for k in ("group_size", "ac", "nights") if state.get(k) is None]
        if wants_rooms(state["user_input"]) and missing:
            text += f"\n(For a room plan I still need: {', '.join(missing)}.)"
    return {"answer": text, "messages": [{"role": "assistant", "content": text}]}


def build_graph():
    g = StateGraph(State)
    g.add_node("understand", understand)
    g.add_node("rag", rag)
    g.add_node("rooms", rooms)
    g.add_node("approval", approval)
    g.add_node("answer", answer)
    g.add_edge(START, "understand")
    g.add_edge("understand", "rag")
    g.add_conditional_edges("rag", route_after_rag, {"rooms": "rooms", "answer": "answer"})
    g.add_conditional_edges("rooms", route_after_rooms, {"approval": "approval", "answer": "answer"})
    g.add_edge("approval", "answer")
    g.add_edge("answer", END)
    return g.compile(checkpointer=MemorySaver())


graph = build_graph()

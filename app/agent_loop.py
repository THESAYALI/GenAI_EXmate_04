"""Day 09 / S1 - hand-written agent loop (no framework).

Loop:  think -> pick a tool -> run it -> read the observation -> think again -> final answer.
Tools: search_docs (your RAG search from Day 07/08) and plan_sansthan_rooms (app/tools.py).

If an LLM wrapper (app/llm.py) is available it decides the next step as JSON.
If not (no key / offline), a small rule-based planner makes the same decisions,
so the loop always runs. Run:  python -m app.agent_loop
"""
import json
import re

from app.tools import plan_sansthan_rooms

MAX_STEPS = 5

SYSTEM = """You are ShirdiYatra, an agent that plans Shirdi trips from official Sansthan data.
Tools:
  search_docs(query)                          -> facts: timings, rules, how to reach
  plan_sansthan_rooms(group_size, ac, nights) -> cheapest Sansthan room mix and total cost
Reply with ONE JSON object only:
  {"action":"tool","tool":"search_docs","args":{"query":"..."}}
  {"action":"tool","tool":"plan_sansthan_rooms","args":{"group_size":7,"ac":true,"nights":2}}
  {"action":"final","answer":"..."}
Never invent prices or timings; use tool results. If the data does not contain the answer, say "I don't know"."""


# ---------- adapters: connect to YOUR existing code here ----------
def search_docs(query, k=4):
    """Wrap your RAG retrieval. Tries common function names from app/rag.py / vectorstore.py."""
    import importlib
    for mod_name, fn_names in (("app.rag", ("retrieve", "search", "retrieve_chunks", "get_chunks")),
                               ("app.vectorstore", ("search", "query", "semantic_search"))):
        try:
            mod = importlib.import_module(mod_name)
        except Exception:
            continue
        for fn_name in fn_names:
            fn = getattr(mod, fn_name, None)
            if callable(fn):
                try:
                    hits = fn(query, k)
                except TypeError:
                    hits = fn(query)
                return [_norm_hit(h) for h in list(hits)[:k]]
    return [{"text": "(RAG search not connected - edit search_docs() in app/agent_loop.py)", "source": ""}]


def _norm_hit(h):
    if isinstance(h, str):
        return {"text": h, "source": ""}
    if isinstance(h, dict):
        meta = h.get("metadata") or {}
        return {"text": h.get("text") or h.get("document") or h.get("chunk") or str(h),
                "source": h.get("source") or h.get("source_url") or meta.get("source", "")}
    return {"text": getattr(h, "text", str(h)), "source": getattr(h, "source", "")}


def call_llm(prompt):
    """Wrap app/llm.py. Returns text, or None if no LLM is usable."""
    try:
        import importlib
        mod = importlib.import_module("app.llm")
        for name in ("generate", "chat", "ask_llm", "call_llm", "complete", "llm_call"):
            fn = getattr(mod, name, None)
            if callable(fn):
                out = fn(prompt)
                return out if isinstance(out, str) else json.dumps(out)
    except Exception:
        pass
    return None


# ---------- understanding the user's message ----------
def extract_trip_params(text):
    """Pull group_size / ac / nights out of free text. Missing values are left out."""
    t = text.lower()
    out = {}
    m = (re.search(r"(?:family|group|party) of (\d+)", t)
         or re.search(r"(\d+)\s*(?:people|persons|members|pilgrims|adults|of us)", t))
    if m:
        out["group_size"] = int(m.group(1))
    if re.search(r"non[\s-]?ac", t):
        out["ac"] = False
    elif re.search(r"\bac\b|air[\s-]?condition", t):
        out["ac"] = True
    m = re.search(r"(\d+)\s*nights?", t)
    if m:
        out["nights"] = int(m.group(1))
    else:
        m = re.search(r"(\d+)[\s-]*days?", t)
        if m:
            out["nights"] = max(1, int(m.group(1)) - 1)
    return out


def wants_rooms(text):
    return bool(re.search(r"room|stay|accommodat|lodg|sansthan|niwas|ashram|cost|budget", text.lower()))


# ---------- the loop ----------
TOOLS = {"search_docs": lambda a: search_docs(a.get("query", "")),
         "plan_sansthan_rooms": lambda a: plan_sansthan_rooms(a.get("group_size"), a.get("ac"), a.get("nights"))}


def _parse_json(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def _rule_decide(question, steps):
    """Offline planner with the same output format as the LLM."""
    used = {s["tool"] for s in steps}
    params = extract_trip_params(question)
    if "search_docs" not in used:
        return {"action": "tool", "tool": "search_docs", "args": {"query": question}}
    if wants_rooms(question) and {"group_size", "ac", "nights"} <= params.keys() and "plan_sansthan_rooms" not in used:
        return {"action": "tool", "tool": "plan_sansthan_rooms", "args": params}
    return {"action": "final", "answer": format_answer(question, steps)}


def format_answer(question, steps):
    parts = []
    for s in steps:
        if s["tool"] == "plan_sansthan_rooms":
            r = s["result"]
            if r.get("ok"):
                lines = [f"{x['count']} x {x['room_type']} ({x['occupants_per_room']} people each)" for x in r["rooms"]]
                parts.append(f"Cheapest Sansthan rooms for {r['group_size']} people, {r['nights']} night(s): "
                             + "; ".join(lines) + f". Total Rs {r['total_cost']:.0f}.")
            else:
                parts.append("Room plan not possible: " + r["error"])
        elif s["tool"] == "search_docs" and s["result"]:
            top = s["result"][0]
            parts.append(f"From the Sansthan pages: {top['text'][:300]}" + (f" (source: {top['source']})" if top["source"] else ""))
    return "\n".join(parts) or "I don't know."


def run_agent(question, verbose=True):
    steps = []
    for i in range(1, MAX_STEPS + 1):
        decision = None
        llm_out = call_llm(SYSTEM + "\n\nQuestion: " + question +
                           "\nTool results so far: " + json.dumps(steps, default=str) + "\nNext JSON:")
        decision = _parse_json(llm_out)
        if not decision or decision.get("action") not in ("tool", "final"):
            decision = _rule_decide(question, steps)

        if verbose:
            print(f"[step {i}] {decision}")
        if decision["action"] == "final":
            return {"answer": decision.get("answer", ""), "steps": steps}

        name, args = decision.get("tool"), decision.get("args", {})
        if name not in TOOLS:
            steps.append({"tool": name, "args": args, "result": {"error": "unknown tool"}})
            continue
        steps.append({"tool": name, "args": args, "result": TOOLS[name](args)})
    return {"answer": format_answer(question, steps), "steps": steps}


if __name__ == "__main__":
    print("ShirdiYatra agent (type 'quit' to exit)")
    while True:
        q = input("\nYou: ").strip()
        if q.lower() in ("quit", "exit", ""):
            break
        print("\nAgent:", run_agent(q)["answer"])

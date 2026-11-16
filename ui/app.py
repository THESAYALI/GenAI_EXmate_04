"""Day 10 - ShirdiYatra Streamlit UI (everything in one file).

  1. Chat      -> calls your FastAPI backend: POST /ask or POST /agent
  2. Citations -> shown under each answer
  3. Feedback  -> thumbs up / down saved to data/feedback.jsonl
  4. Signature feature: "Shirdi timeline" card - 4 aartis, darshan queue hours and
     prasadalaya hours on a 24-hour clock, with the user's train arrival marked.

Run from the repo root:   streamlit run ui/app.py
"""
import json
import math
import uuid
from datetime import datetime, time
from pathlib import Path

import requests
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
TIMELINE_FILE = ROOT / "data" / "timeline.json"
FEEDBACK_FILE = ROOT / "data" / "feedback.jsonl"


# ============================== timeline logic ==============================
def to_min(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def fmt(minutes):
    minutes %= 1440
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def load_timeline():
    with open(TIMELINE_FILE, encoding="utf-8") as f:
        return json.load(f)


def event_status(data, arrival_min, buffer_min):
    """Which events can the visitor attend? Ready time = train arrival + travel buffer."""
    ready = arrival_min + buffer_min
    rows = []
    for a in data["aartis"]:
        t = to_min(a["time"])
        rows.append({"kind": "Aarti", "name": a["name"], "when": a["time"], "ok": t >= ready})
    for key, label in (("darshan_queue", "Darshan"), ("prasadalaya", "Prasadalaya")):
        for s in data[key]:
            start, end = to_min(s["start"]), to_min(s["end"])
            rows.append({"kind": label, "name": s["name"], "when": f"{s['start']}-{s['end']}",
                         "ok": end > ready, "partial": start < ready < end})
    rows.sort(key=lambda r: to_min(r["when"].split("-")[0]))
    return rows, ready


def _pt(cx, cy, r, minutes):
    ang = math.radians(minutes / 1440 * 360 - 90)         # 00:00 at the top, clockwise
    return cx + r * math.cos(ang), cy + r * math.sin(ang)


def _arc(cx, cy, r, m1, m2, color, width):
    x1, y1 = _pt(cx, cy, r, m1)
    x2, y2 = _pt(cx, cy, r, m2)
    large = 1 if (m2 - m1) % 1440 > 720 else 0
    return (f'<path d="M {x1:.1f} {y1:.1f} A {r} {r} 0 {large} 1 {x2:.1f} {y2:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="butt" opacity="0.85"/>')


def clock_svg(data, arrival_min=None, ready_min=None):
    """A 24-hour clock: outer ring = darshan queue, inner ring = prasadalaya,
    dots = aartis, red needle = train arrival, dashed needle = ready to enter Sansthan."""
    cx = cy = 200
    s = [f'<svg viewBox="0 0 400 400" width="100%" style="max-width:460px" xmlns="http://www.w3.org/2000/svg">',
         f'<circle cx="{cx}" cy="{cy}" r="185" fill="#fffaf0" stroke="#d9c9a3" stroke-width="2"/>']
    for h in range(24):                                     # hour ticks + labels
        x1, y1 = _pt(cx, cy, 175, h * 60)
        x2, y2 = _pt(cx, cy, 183 if h % 6 == 0 else 179, h * 60)
        s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#8a7a55" stroke-width="{2 if h % 6 == 0 else 1}"/>')
        if h % 3 == 0:
            lx, ly = _pt(cx, cy, 160, h * 60)
            s.append(f'<text x="{lx:.1f}" y="{ly + 4:.1f}" font-size="11" text-anchor="middle" fill="#5c4d2a">{h:02d}</text>')
    for q in data["darshan_queue"]:
        s.append(_arc(cx, cy, 140, to_min(q["start"]), to_min(q["end"]), "#f4b400", 14))
    for p in data["prasadalaya"]:
        s.append(_arc(cx, cy, 115, to_min(p["start"]), to_min(p["end"]), "#34a853", 14))
    for a in data["aartis"]:
        t = to_min(a["time"])
        x, y = _pt(cx, cy, 140, t)
        lx, ly = _pt(cx, cy, 82, t)
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="#c0392b" stroke="white" stroke-width="2"/>')
        s.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="9" text-anchor="middle" fill="#7b241c">{a["name"].split()[0]}</text>')
        s.append(f'<text x="{lx:.1f}" y="{ly + 10:.1f}" font-size="9" text-anchor="middle" fill="#7b241c">{a["time"]}</text>')
    if ready_min is not None:
        x, y = _pt(cx, cy, 170, ready_min)
        s.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#1a73e8" stroke-width="2" stroke-dasharray="5 4"/>')
    if arrival_min is not None:
        x, y = _pt(cx, cy, 175, arrival_min)
        s.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#d93025" stroke-width="3"/>')
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="#d93025"/>')
        s.append(f'<text x="{cx}" y="{cy + 5}" font-size="13" text-anchor="middle" font-weight="bold" fill="#d93025">Train {fmt(arrival_min)}</text>')
    s.append('</svg>')
    return "".join(s)


def render_timeline_card():
    st.subheader("Shirdi timeline - what can you attend?")
    try:
        data = load_timeline()
    except Exception as e:
        st.error(f"Could not read data/timeline.json: {e}")
        return
    c1, c2 = st.columns(2)
    arrival = c1.time_input("Your train arrives at Kopargaon / Shirdi", value=time(9, 30), key="arrival")
    buffer_min = c2.slider("Minutes to reach Sansthan", 0, 180, 60, 15, key="buffer")
    arrival_min = arrival.hour * 60 + arrival.minute
    rows, ready = event_status(data, arrival_min, buffer_min)

    left, right = st.columns([3, 2])
    with left:
        st.markdown(clock_svg(data, arrival_min, ready), unsafe_allow_html=True)
        st.caption("Red dots = aartis | yellow ring = darshan queue | green ring = prasadalaya | "
                   "red needle = train arrival | blue dashed = you are ready at Sansthan")
    with right:
        st.markdown(f"**Ready at Sansthan by {fmt(ready)}**")
        for r in rows:
            if r["ok"]:
                icon = "🟡" if r.get("partial") else "✅"
                note = " (in progress)" if r.get("partial") else ""
            else:
                icon, note = "❌", " (missed today)"
            st.write(f"{icon} {r['name']} - {r['when']}{note}")
        st.caption(f"Source: {data.get('source_url', '')} | checked on {data.get('checked_on', '?')}")


# ================================ chat logic ================================
def call_backend(base_url, mode, question, thread_id):
    """POST to /ask or /agent. Returns (json, error)."""
    try:
        if mode == "/agent":
            payload = {"message": question, "thread_id": thread_id}
        else:
            payload = {"question": question, "query": question}
        r = requests.post(base_url.rstrip("/") + mode, json=payload, timeout=120)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, f"Backend error: {e}"


def resume_agent(base_url, thread_id, approve):
    try:
        r = requests.post(base_url.rstrip("/") + "/agent", json={"thread_id": thread_id, "approve": approve}, timeout=120)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, f"Backend error: {e}"


def extract_answer_and_citations(resp):
    """Be tolerant about the response shape of /ask and /agent."""
    answer = resp.get("answer") or resp.get("response") or resp.get("text") or json.dumps(resp, indent=2)
    cites = resp.get("citations") or resp.get("sources") or []
    out = []
    for c in cites:
        if isinstance(c, str):
            out.append(c)
        elif isinstance(c, dict):
            label = c.get("title") or c.get("source") or c.get("source_url") or c.get("url") or ""
            url = c.get("source_url") or c.get("url") or c.get("source") or ""
            out.append(f"{label} - {url}" if url and url != label else label)
    return answer, [c for c in out if c]


def save_feedback(rating, question, answer, mode):
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    row = {"time": datetime.now().isoformat(timespec="seconds"), "rating": rating,
           "mode": mode, "question": question, "answer": answer}
    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def feedback_buttons(idx, question, answer, mode):
    key = f"fb_{idx}"
    if st.session_state.get(key):
        st.caption(f"Feedback saved: {st.session_state[key]}")
        return
    c1, c2, _ = st.columns([1, 1, 8])
    if c1.button("👍", key=f"up_{idx}"):
        save_feedback("up", question, answer, mode)
        st.session_state[key] = "👍"
        st.rerun()
    if c2.button("👎", key=f"down_{idx}"):
        save_feedback("down", question, answer, mode)
        st.session_state[key] = "👎"
        st.rerun()


def add_assistant(resp, question, mode):
    answer, cites = extract_answer_and_citations(resp)
    st.session_state.history.append({"role": "assistant", "content": answer, "citations": cites,
                                     "question": question, "mode": mode})


def render_chat():
    st.subheader("Ask ShirdiYatra")
    for i, m in enumerate(st.session_state.history):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m["role"] == "assistant":
                if m.get("citations"):
                    with st.expander("Citations"):
                        for c in m["citations"]:
                            st.write("- " + c)
                feedback_buttons(i, m.get("question", ""), m["content"], m.get("mode", ""))

    pending = st.session_state.get("pending")            # /agent approval step
    if pending:
        st.info("The agent needs your approval for this room plan:")
        st.json(pending["proposal"])
        a, b = st.columns(2)
        for label, flag, col in (("Approve", True, a), ("Reject", False, b)):
            if col.button(label, key=f"approve_{flag}"):
                resp, err = resume_agent(st.session_state.base_url, st.session_state.thread_id, flag)
                st.session_state.pending = None
                if err:
                    st.session_state.history.append({"role": "assistant", "content": err})
                else:
                    add_assistant(resp, pending["question"], "/agent")
                st.rerun()
        return

    q = st.chat_input("Ask about aarti timings, rooms, how to reach Shirdi ...")
    if q:
        st.session_state.history.append({"role": "user", "content": q})
        with st.spinner("Thinking ..."):
            resp, err = call_backend(st.session_state.base_url, st.session_state.mode, q, st.session_state.thread_id)
        if err:
            st.session_state.history.append({"role": "assistant", "content": err})
        elif resp.get("status") == "awaiting_approval":
            st.session_state.pending = {"proposal": resp["proposal"], "question": q}
        else:
            add_assistant(resp, q, st.session_state.mode)
        st.rerun()


# ================================== page ==================================
def main():
    st.set_page_config(page_title="ShirdiYatra", page_icon="🛕", layout="wide")
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("thread_id", str(uuid.uuid4())[:8])
    st.session_state.setdefault("pending", None)

    with st.sidebar:
        st.title("🛕 ShirdiYatra")
        st.caption("Plan your Shirdi visit from official Sansthan pages")
        st.session_state.base_url = st.text_input("Backend URL", "http://127.0.0.1:8000")
        st.session_state.mode = st.radio("Endpoint", ["/ask", "/agent"], help="/ask = RAG answer, /agent = tools + approval")
        if st.button("New conversation"):
            st.session_state.history, st.session_state.pending = [], None
            st.session_state.thread_id = str(uuid.uuid4())[:8]
            st.rerun()
        st.caption(f"thread: {st.session_state.thread_id}")

    tab_chat, tab_timeline = st.tabs(["💬 Chat", "🕒 Shirdi timeline"])
    with tab_chat:
        render_chat()
    with tab_timeline:
        render_timeline_card()


if __name__ == "__main__":
    main()

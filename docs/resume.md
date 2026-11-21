# Resume bullets — ShirdiYatra

Replace every {placeholder} with your real number before using. Keep each bullet to one or two lines.

**ShirdiYatra — RAG travel assistant for Shirdi pilgrims** · Python, FastAPI, Chroma, LangGraph, Streamlit, Docker · github.com/THESAYALI/GenAI_EXmate_04 · {live URL}

- Built a retrieval-augmented assistant over official Sai Sansthan pages (20 structured records with source URLs and verified-on dates), serving cited answers through a FastAPI `/ask` endpoint and refusing unanswerable questions; lifted accuracy on a 15-question eval set from {A}/15 to {B}/15 by tuning chunk size and top-k.
- Designed a LangGraph agent with a human-approval step and a deterministic room-planning tool (cheapest room mix for a group, tariff rules enforced in pure Python), plus a Streamlit one-day timeline card that maps aarti and darshan timings to the user's train arrival.
- Productionised the service: GitHub Actions CI (ruff, pytest, Docker build), public deployment on {Render / Hugging Face Spaces}, per-request latency and token logging, a TTL cache that cut repeat-question latency from {X} ms to {Y} ms, input limits, and a tested prompt-injection guard.

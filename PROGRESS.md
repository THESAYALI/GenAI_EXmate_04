# PROGRESS: ShirdiYatra (SJ-50)

Tick a box only when you have checked it yourself (open the file, run the command, or open the link).
Change `[ ]` to `[x]` and fill the evidence column or line.

## Day-by-day status

| Day | Task | Evidence (file / link) | Done |
|-----|------|------------------------|------|
| D1 | README project card, day01_intro.py, day01_menu.py | `README.md`, `day01/` | [ ] |
| D2 | data/sample_records.json, app/records.py, app/cli.py, requirements.txt, .gitignore | `app/`, `data/` at repo root | [ ] |
| D3 | Real data: app/fetch.py, ingest.py, models.py, data/raw, data/records.json | `data/records.json` | [ ] |
| D4 | FastAPI: /health, /records, /search, POST /questions | `app/main.py` | [ ] |
| D5 | docs/how_llms_work.md, eval/questions.md (10 questions, Q6 unanswerable), tag checkpoint-1 | `docs/`, `eval/` | [ ] |
| D6 | app/llm.py, POST /chat, prompts/, eval/prompt_compare.md, .env.example | `app/llm.py`, `prompts/` | [ ] |
| D7 | app/chunking.py, embed.py, vectorstore.py, GET /search/semantic, eval/search_results.md | `eval/search_results.md` | [ ] |
| D8 | app/rag.py, POST /ask with citations, eval/eval_set.json, eval/run_eval.py, winner table in README | README table | [ ] |
| D9 | app/tools.py (plan_sansthan_rooms), agent_loop.py, graph.py, POST /agent | `day09/README.md` | [ ] |
| D10 | ui/app.py Streamlit, citations, thumbs up/down, timeline card, screenshot, tag checkpoint-2 | README screenshot | [ ] |
| D12 | ci.yml (ruff, pytest, docker build), green badge, PR #1 merged, live deploy, /health public | Actions page, live URL | [ ] |
| D13 | Latency + token logs, cache, input limits, injection test, Production notes, README, docs/resume.md | README, `docs/resume.md` | [ ] |
| D14 | docs/interview.md, PROGRESS.md closed, demo rehearsed twice, tag final | this file | [ ] |

## Open items to close (D14)

- [ ] `docs/interview.md` has no `[FILL]` left
- [ ] README has no `YOUR-HF-USERNAME` left and shows the real live URL
- [ ] Live `/health` returns OK in an incognito window (URL: ____________________)
- [ ] CI badge on README is green on `main`
- [ ] PR #1 (`feature/day-12-ci`) is merged
- [ ] README has the eval winner table (2 configs, 15 questions)
- [ ] README "Production notes" has real numbers (latency, tokens, cache)
- [ ] `docs/resume.md` has 3 resume bullets
- [ ] Live URL added to the tracker
- [ ] Demo rehearsal 1 done (see `docs/demo_rehearsal.md`)
- [ ] Demo rehearsal 2 done
- [ ] `git tag final` pushed

## Known limits (honest notes)

- Free Render tier sleeps; first request can take about a minute.
- `data/chroma/` is in `.gitignore`, so the deployed app needs the index built at startup or ingested on deploy: __________ (write what you did)
- Data is only as fresh as each record's "checked on" date.

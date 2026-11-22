# Day 14: Interview Prep, Closing the Project and Final Tag

**Project:** ShirdiYatra (SJ-50), a RAG assistant for planning a Shirdi visit from official Sai Baba Sansthan pages
**Date:** Mon 23 Nov
**Student:** Sayali Rajendra Pawar (CSE)
**Repo:** https://github.com/THESAYALI/GenAI_EXmate_04

---

## 1. What the Day 14 task says

> `docs/interview.md`: your 60-second pitch for ShirdiYatra and answers to 10 likely questions. Your interview story (hardest problem): prices and rules change and appear in several versions (English, Hindi, Marathi pages, older copies on mirror domains), and the site warns about fake look-alike websites. Ingestion must keep only official domains, store a 'checked on' date per record, and parse HTML tariff tables into clean numbers. Close every open item in `PROGRESS.md`, rehearse the demo twice, tag final.

In plain words, the task has **five jobs**:

| # | Job | Output |
|---|-----|--------|
| 1 | Write a 60-second pitch | section in `docs/interview.md` |
| 2 | Write answers to 10 likely interview questions | section in `docs/interview.md` |
| 3 | Write the interview story about the hardest problem | section in `docs/interview.md` |
| 4 | Close every open item in `PROGRESS.md` | updated `PROGRESS.md` |
| 5 | Rehearse the demo twice, then tag `final` | `docs/demo_rehearsal.md` and a git tag |

Day 14 is different from the earlier days. There is almost no new feature code. The goal is to **explain, prove and finish** the project you already built, the way you would in a real job interview.

---

## 2. Files for this day

| File | Folder | Purpose |
|------|--------|---------|
| `interview.md` | `docs/` | pitch, 10 Q&A, hardest-problem story, demo script |
| `PROGRESS.md` | repo root (next to `README.md`) | day-by-day tracker and list of open items |
| `demo_rehearsal.md` | `docs/` | demo script and two rehearsal logs |
| `final_check.ps1` | `scripts/` | PowerShell check before tagging |
| `README.md` (this file) | `day14/` | full explanation of the task |

Your repo root is `C:\Users\Sayali Pawar\Desktop\GenAI_EXmate_04_clean`.

---

## 3. Job 1: The 60-second pitch

### What it is
A **pitch** is a short, spoken summary that tells someone what your project is, why it matters and why you are the right person to explain it. In interviews the first question is often "tell me about your project", and this is your answer.

### Why 60 seconds
About 150 words is what a person speaks in one minute. Longer than that and the interviewer loses interest. Shorter and you skip the important parts.

### The 5-part structure
1. **Problem:** what hurts, and for whom.
2. **Solution:** what you built, in one sentence.
3. **How it works:** two or three technical points.
4. **Special features:** what makes it yours.
5. **Proof:** tests, deployment, numbers.

### How to practise
Read it aloud with a timer. If it takes more than 70 seconds, cut words. Do not memorise it word for word. Learn the five parts and say them naturally.

---

## 4. Job 2: Ten likely interview questions

### What the task wants
Interviewers do not read your code first. They ask questions to see if you **understand** what you built. For each question you need a short, honest answer in your own words.

### The ten topics covered
| # | Topic | What the interviewer is checking |
|---|-------|----------------------------------|
| 1 | Problem and users | Do you know why this exists? |
| 2 | Why RAG, not just an LLM | Do you understand hallucination? |
| 3 | How retrieval works | Do you understand chunks, embeddings and top-k? |
| 4 | Stopping made-up answers | Do you care about correctness? |
| 5 | Evaluation | Did you measure, or just guess? |
| 6 | Why a tool for rooms | Do you know LLM limits with maths and rules? |
| 7 | Agent: hand-written vs LangGraph | Did you understand what the framework does? |
| 8 | Testing and deployment | Can you ship software? |
| 9 | Production safety | Latency, tokens, cache, input limits, prompt injection |
| 10 | What you would improve | Can you think beyond what you built? |

### Rule for answers
Every number in your answer (latency, eval score, live URL) must be a **real value from your project**. In `interview.md` these are marked `[FILL]`. Replace each one before you tag final.

---

## 5. Job 3: The interview story (hardest problem)

### What it is
Many interviews ask: "Tell me about the hardest problem you solved." The standard way to answer is the **STAR method**:

| Letter | Meaning | In your project |
|--------|---------|-----------------|
| **S** | Situation | Shirdi information exists in many versions and fake sites exist |
| **T** | Task | Make sure every answer comes from the current official source |
| **A** | Action | Official domains only, 'checked on' date, parse tariff tables |
| **R** | Result | Cited, dated answers, computed room costs, honest "I don't know" |

### The real problem in your project
Prices and rules at Shirdi **change over time**, and the same information is found in:
- English, Hindi and Marathi pages (the versions may not match),
- older copies on mirror domains (other websites that copy the page),
- fake look-alike websites (the Sansthan site itself warns about these).

If your app mixed in a wrong copy, a pilgrim could get a wrong room price or timing. That is a real-world harm, not just a bug.

### The three required fixes, explained

**1. Keep only official domains**
Ingestion (the step that downloads and stores data) must accept only the official Sansthan domain, `sai.org.in`. Any other domain is dropped. This is called an **allow-list**: you list what is allowed instead of trying to list everything that is bad.
*Why:* it blocks fake sites and old mirror copies at the entrance.

**2. Store a 'checked on' date per record**
Each record gets a field such as `checked_on: 2026-11-21`.
*Why:* data goes stale. With this date, the app (and the user) can see how fresh an answer is, and you know when to re-check.

**3. Parse HTML tariff tables into clean numbers**
The room prices on the website are in an HTML `<table>`. Parsing means reading that table with code and converting it into structured fields, for example room type, rate in rupees, min and max capacity and extra-person charge, as **numbers and not text**.
*Why:* text like "Rs. 600/-" cannot be added or compared. Numbers can. This is what makes the `plan_sansthan_rooms` tool possible.

### What the story must show an interviewer
- You found a real risk (wrong data), not just a coding error.
- You solved it with design choices (allow-list, dates, structure).
- You tested it (including the question the data cannot answer).
- You can say what you learned.

---

## 6. Job 4: Close every open item in `PROGRESS.md`

### What `PROGRESS.md` is
A tracker file in the repo root. It lists each day's task, the evidence (file or link) and whether it is done.

### What "close" means
An item is **closed** only when you have **checked it yourself**:
- a file: open it and see it exists and is correct,
- a command: run it and see the output,
- a link: open it in the browser.

Do not tick a box because you "think" it is done.

### The open items for Day 14
| Item | How to verify |
|------|---------------|
| No `[FILL]` left in `interview.md` | search the file for `[FILL` |
| README has the real live URL | search README for `YOUR-HF-USERNAME`, it must find nothing |
| Live `/health` works publicly | open `<live-url>/health` in an incognito window |
| CI badge is green on `main` | check the badge and the Actions page |
| PR #1 is merged | open Pull requests, closed tab |
| Eval winner table in README | the table with 2 configs, 15 questions |
| Production notes have real numbers | latency, tokens, cache in README |
| `docs/resume.md` has 3 bullets | open the file |
| Live URL in the tracker | check the tracker |
| Demo rehearsed twice | fill both logs in `docs/demo_rehearsal.md` |
| `git tag final` pushed | run `git ls-remote --tags origin` |

---

## 7. Job 5: Rehearse the demo twice, then tag final

### What a demo is
A live show of your working project. In an interview or checkpoint you usually have about 2 minutes, and anything can go wrong (slow internet, sleeping server, API errors).

### Why twice
The first run finds the problems. The second run proves you fixed them.

### The demo script
1. Show `/health` returning OK on the live URL.
2. Ask a normal question (for example, aarti timings) and point to the citation.
3. Ask the Q6 question that the data cannot answer, and show "I don't know".
4. Ask for rooms for 7 people for 2 nights and show the cheapest mix and total.
5. Show the timeline card with the train arrival time marked.
6. Open GitHub Actions and show the green CI badge.

### Plan B (if something fails)
- **Server asleep:** the free Render tier sleeps when unused. Open `/health` one minute before the demo.
- **LLM or API error:** show a saved screenshot and explain the flow from `app/rag.py`.
- **Internet problem:** run locally with `uvicorn app.main:app --reload` and `streamlit run ui/app.py`.

### What `git tag final` means
A **git tag** is a permanent label on one specific commit. Branches move as you commit, but a tag stays. Tagging `final` says: "this exact commit is my finished project." Earlier you used `checkpoint-1` and `checkpoint-2` the same way.

---

## 8. Glossary: every term in this task

| Term | Meaning |
|------|---------|
| **Pitch** | short spoken summary of your project |
| **STAR method** | Situation, Task, Action, Result, a way to tell an interview story |
| **RAG** | Retrieval-Augmented Generation: find relevant text first, then let the LLM answer from it |
| **LLM** | Large Language Model, the AI that writes the answer |
| **Hallucination** | when an LLM states something wrong with confidence |
| **Chunk** | a small piece of a document, stored with its source, page and title |
| **Embedding** | a list of numbers that represents the meaning of text, used for semantic search |
| **Vector database (Chroma)** | a database that finds the chunks closest in meaning to a question |
| **top-k** | how many best-matching chunks are sent to the LLM |
| **Citation** | showing which source the answer came from |
| **Evaluation (eval)** | testing the system on a fixed question set and scoring the results |
| **Ingestion** | downloading, cleaning and storing the data |
| **Official domain** | the real Sansthan website, `sai.org.in` |
| **Mirror domain** | another website that copies a page, so it may be old or wrong |
| **Look-alike website** | a fake site that imitates the official one |
| **Allow-list** | a list of the only domains you accept |
| **'checked on' date** | the date a record was last verified against the source |
| **Parsing** | reading structured content (like an HTML table) with code |
| **HTML tariff table** | the price table on the website, written in HTML |
| **Tool (`plan_sansthan_rooms`)** | a plain Python function that the app or agent can call |
| **Agent** | a program where the LLM chooses which tool to use next |
| **LangGraph** | a library that models an agent as a graph with memory and approval steps |
| **FastAPI** | the Python framework for the backend API |
| **Streamlit** | the Python framework for the chat user interface |
| **CI (Continuous Integration)** | automatic checks that run on every push |
| **GitHub Actions** | GitHub's CI system, configured in `.github/workflows/ci.yml` |
| **ruff** | a fast Python style checker |
| **pytest** | a Python testing tool |
| **Docker build** | building the app's container image to prove it can be packaged |
| **Deploy** | putting the app on the internet, here on Render |
| **`render.yaml`** | Render's recipe file that describes how to run the app |
| **`/health`** | a simple URL that returns OK if the app is running |
| **Prompt injection** | a user message that tries to trick the model into ignoring its rules |
| **Latency** | time taken to answer one request |
| **Token** | a small unit of text the LLM reads or writes, which determines cost and speed |
| **Cache** | stored answers reused so repeated questions are faster |
| **Git tag** | a permanent label on one commit |
| **PROGRESS.md** | the tracker of what is done and what is open |

---

## 9. Step-by-step: how to finish Day 14

1. **Save the files** in the right folders (section 2).
2. **Open `docs/interview.md`** and replace every `[FILL]` with a real value.
3. **Read every answer once** and change any sentence that is not true for your code. You must be able to explain each line in your own words.
4. **Update `PROGRESS.md`:** verify each item yourself, then tick it.
5. **Rehearse the demo** using `docs/demo_rehearsal.md`. Write the time and the problems after each run.
6. **Run the final check** from the repo root:

```powershell
cd "C:\Users\Sayali Pawar\Desktop\GenAI_EXmate_04_clean"
powershell -ExecutionPolicy Bypass -File scripts\final_check.ps1 -LiveUrl "https://your-app.onrender.com"
```

7. **Commit and push:**

```powershell
git add docs/interview.md docs/demo_rehearsal.md PROGRESS.md scripts/final_check.ps1 day14/README.md
git commit -m "day-14: interview prep, close PROGRESS items, final checks"
git push
```

8. **Wait for CI to turn green** on the Actions page.
9. **Tag and push the tag:**

```powershell
git tag final
git push origin final
```

---

## 10. Common problems and fixes

| Problem | Fix |
|---------|-----|
| `final_check.ps1` shows `YOUR-HF-USERNAME` | open README, replace with the real live URL |
| `/health` fails or is slow | free tier is waking up, wait one minute and try again |
| `git tag final` says "already exists" | `git tag -d final`, then tag again after your last commit |
| `git push origin final` rejected | delete the old remote tag: `git push origin :refs/tags/final`, then push again |
| CI is red after the push | open the failed run, read the red line and fix it before tagging |
| Browser added "(1)" to file names | rename the file and remove the "(1)" |
| `scripts` folder is missing | `mkdir scripts` in the repo root |

---

## 11. Final self-check (all must be yes)

- [ ] I can say the pitch in about 60 seconds without reading.
- [ ] I can explain every answer in `interview.md` in my own words.
- [ ] I can tell the hardest-problem story using Situation, Task, Action, Result.
- [ ] My README has the real live URL and `/health` works publicly.
- [ ] CI is green and PR #1 is merged.
- [ ] Every item in `PROGRESS.md` is verified and ticked.
- [ ] I rehearsed the demo twice and know my Plan B.
- [ ] `final` tag is pushed.
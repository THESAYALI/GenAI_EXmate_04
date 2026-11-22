# ShirdiYatra: Interview Prep

> Replace every **[FILL]** with your real number or name before you tag final.

## 1. The 60-second pitch (about 150 words, read it aloud once)

"Pilgrims planning a Shirdi trip have a real problem: aarti timings, darshan hours and room prices are spread across many pages, and some of those pages are fake look-alike websites. I built **ShirdiYatra**, an assistant that answers trip questions only from the official Sai Baba Sansthan website.

It collects the official pages, cleans them into records with a 'checked on' date, and splits them into chunks stored in a Chroma vector database. When you ask a question, it retrieves the best chunks and the LLM answers with citations. If the data does not contain the answer, it says 'I don't know' instead of guessing.

It also has a tool, `plan_sansthan_rooms`, that finds the cheapest room mix for a group, and a one-day timeline card that shows which aartis you can attend based on your train arrival time.

It is built with FastAPI and Streamlit, tested with an evaluation set, checked by CI with GitHub Actions, and deployed live on Render."

## 2. Ten likely interview questions

**Q1. What problem does ShirdiYatra solve, and who is it for?**
A family planning a first 2-day Shirdi trip (my example persona: 7 people from Hyderabad, with grandparents, arriving by train to Kopargaon) needs reliable timings and room prices. The information is spread over many pages and some copies are outdated or fake. My app gives one cited answer from the official source.

**Q2. Why RAG instead of just asking an LLM?**
An LLM can sound confident and still give a wrong aarti time or room price. RAG makes the model answer from retrieved official text and show the source. It also lets me update the data without retraining anything.

**Q3. How does your retrieval work?**
I chunk the documents and keep the source, page and title with each chunk. Then I create embeddings with sentence-transformers and store them in a persistent Chroma collection. At question time I embed the question, fetch the top-k closest chunks and pass them to the LLM as context.

**Q4. How do you stop the model from making things up?**
The prompt tells it to answer only from the retrieved chunks and to cite them. My evaluation set includes a question the data cannot answer (Q6), and the correct behaviour is "I don't know". I check that on every evaluation run.

**Q5. How did you evaluate your system?**
I made `eval/eval_set.json` with 15 questions and ran `eval/run_eval.py` on two configurations (different chunk size and top-k). I compared them in a table in the README. The winner was **[FILL: config and score]**.

**Q6. Why did you build a tool for rooms instead of letting the LLM calculate?**
LLMs are unreliable with arithmetic and rules. `plan_sansthan_rooms` is plain Python: it takes group size, AC or non-AC and number of nights, uses min and max room capacity, rate and extra-person charge, and returns the cheapest valid mix and total cost. Rules like "no single-person rooms" are enforced in code, so the answer is the same every time and easy to test.

**Q7. What is the difference between your hand-written agent and the LangGraph version?**
The hand-written loop in `agent_loop.py` showed me the basic cycle: the model picks a tool, I run it, and I give the result back. The LangGraph version in `graph.py` makes the same flow explicit as a graph and adds memory and one human approval step before the final action. Building it by hand first helped me understand what LangGraph does for me.

**Q8. How do you test and deploy it?**
GitHub Actions runs `ruff` (style), `pytest` (tests) and a `docker build` on every push. I worked on a feature branch, opened PR #1 and merged it after CI was green. The app is deployed on Render using `render.yaml`, and `/health` works publicly. Live URL: **[FILL]**.

**Q9. What did you do for production safety?**
I log latency and token use for each request, added a simple cache, put limits on input size and wrote a prompt-injection test. The README "Production notes" section has my numbers: average latency **[FILL] s**, cache hit effect **[FILL]**.

**Q10. What would you improve next?**
First, refresh the data on a schedule so the 'checked on' date stays current. Second, add the Hindi and Marathi official pages. Third, add more evaluation questions and a proper faithfulness check. Fourth, move from the free hosting tier to something without cold starts.

## 3. Interview story: the hardest problem

**Situation.** Shirdi prices and rules change, and the same information exists in several versions: English, Hindi and Marathi pages, and older copies on mirror domains. The Sansthan site itself warns about fake look-alike websites. If my app mixed in a wrong copy, a pilgrim could get the wrong room price or timing.

**Task.** I had to make sure every answer came from the current official source and that a user could see how fresh it was.

**Action.**
- I allowed only official domains in ingestion and dropped anything else.
- I stored a **'checked on' date** with every record, so each answer can show how recent the data is.
- Tariff tables are in HTML, so I parsed them into clean numbers (rate, capacity, extra-person charge) instead of leaving them as text. This is what made the room-planning tool possible.
- I added an evaluation question the data cannot answer to check that the app says "I don't know".

**Result.** Answers come with a source and a date, room costs are computed from structured numbers, and unknown questions get an honest "I don't know". **[FILL: one real number, e.g. records ingested or eval score]**

**What I learned.** For real-world data, trust and freshness matter as much as the model. Most of the quality came from cleaning the data and enforcing rules in code, not from the prompt.

## 4. Demo script (rehearse twice, about 2 minutes)

1. Open the live URL and show `/health` returning OK.
2. Ask a normal question (for example, today's aarti timings) and point to the citation.
3. Ask the question the data cannot answer and show "I don't know".
4. Ask for rooms for 7 people for 2 nights and show the cheapest mix and total.
5. Show the timeline card with a train arrival time marked.
6. Open the GitHub Actions page and show the green CI badge.

**If something goes wrong:** the free Render tier may be asleep, so open `/health` 1 minute before the demo. Keep a screenshot of each step as a backup.

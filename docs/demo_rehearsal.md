# Demo rehearsal log

Goal: a clean 2-minute demo that does not depend on luck.

## Before every run (1 minute)
- [ ] Open the live `/health` link so Render is awake
- [ ] Local backup ready: `uvicorn app.main:app --reload` and `streamlit run ui/app.py`
- [ ] Screenshots of each step saved as backup
- [ ] Phone silent, notifications off, browser zoom at 110%

## Script
1. Show `/health` returning OK on the live URL.
2. Ask: "What are the aarti timings?" Point to the citation.
3. Ask the Q6 question the data cannot answer. Show "I don't know".
4. Ask: "Cheapest rooms for 7 people, 2 nights." Show the room mix and total cost.
5. Show the timeline card with the train arrival time marked.
6. Open GitHub Actions and show the green CI badge.

## Rehearsal 1
- Date / time: ____________   Total time: ______ min
- What went wrong: ______________________________
- What I will fix: ______________________________

## Rehearsal 2
- Date / time: ____________   Total time: ______ min
- What went wrong: ______________________________
- What I will fix: ______________________________

## If it fails during the real demo
- Live site slow: say "free tier is waking up", switch to the local copy.
- LLM error: show the screenshot and explain the flow from `app/rag.py`.
- Be ready to explain ONE function in your own words (suggested: `plan_sansthan_rooms`).

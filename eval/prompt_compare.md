# Prompt comparison: v1 vs v2

Generated on 13 Nov 2026 11:29 by `eval/run_compare.py` (provider: **groq**, model: **openai/gpt-oss-20b**, temperature 0.2).

## The two prompt versions

| | v1 (`prompts/task_answer_v1.md`) | v2 (`prompts/task_answer_v2.md`) |
|---|---|---|
| Style | Short and simple: question + records + one instruction | Step by step with 5 steps, rules for each confidence level and 2 format examples |
| Handles missing data | Only the general rule in the system prompt | Explicit step: do not use a nearby record, answer "low" |
| Handles live questions | Not mentioned | Explicit: queue, crowd and availability need live data |
| Follow-up | Free choice | Must help a family planning a trip |
| Cost | Fewer tokens | More tokens per call |

## Summary

| Check | v1 | v2 |
|---|---|---|
| Valid JSON replies | 10/10 | 10/10 |
| Replies with confidence "low" | 5 | 5 |
| Confidence on Q6 (must be low) | low | low |

## Results per question

| # | Question | v1 answer | v1 conf. | v2 answer | v2 conf. |
|---|---|---|---|---|---|
| 1 | What time is the Kakad aarti at Shirdi? | The Kakad Aarti at Shirdi is held at 5:15 AM. | high | The Kakad Aarti (Morning) is held at 5:15 AM (source: https://sai.org.in/en/daily-programme). | high |
| 2 | What are the darshan timings for Shirdi Sai Baba temple? | Darshan at the Samadhi Mandir begins at 6:25 AM (as per the daily programme). | high | Darshan at the Samadhi Mandir starts at 6:25 AM (source: https://sai.org.in/en/daily-programme). | high |
| 3 | How can a family of 7 reach Shirdi from Hyderabad by train? | I do not have information on train routes from Hyderabad to Shirdi in the provided records. | low | I don't have that information in my data. | low |
| 4 | Which railway station is nearest to Shirdi, and how far is it from the temple? | I do not have that information. | low | I don't have that information in my data. | low |
| 5 | How much does a Sansthan room at Sai Bhakta Niwas cost? | A Sansthan room at Sai Bhakta Niwas costs ₹200 per night. | high | A Sansthan room at Sai Bhakta Niwas costs ₹200 (source: https://sai.org.in/en/accomodations). | high |
| 6 | Which private hotel near Shirdi has a swimming pool, and what is its price? | I do not have that information. | low | I don't have that information in my data. | low |
| 7 | What are the timings of the Madhyan (noon) aarti? | I do not have information on the Madhyan (noon) aarti timing. | low | I don't have that information in my data. | low |
| 8 | Can a single person book a room in Sansthan accommodation? | I do not have a record that explicitly states whether a single person can book a room in Sansthan accommodation. | low | I don't have information on whether a single person can book a room in Sansthan accommodation. | low |
| 9 | What is the cheapest room mix for 7 people staying 2 days? | The cheapest option for 7 people staying 2 days is to book two Dwarawati – noN AC‑WESTERN rooms (capacity 3‑5 each). Each room costs ₹500 per day, so the total cost is ₹1,000 per day or ₹2,000 for the 2‑day stay. (Source: https... | high | The cheapest option is to book two Dwarawati – noN AC‑WESTERN rooms, each costing ₹500 per day. For 7 people over 2 days that totals ₹2,000 (₹1,000 per day). (Source: https://sai.org.in/en/accomodations) | high |
| 10 | What time is the Shej (night) aarti, and when does the temple close? | Shej (night) aarti is held at 10:00 PM (source: https://sai.org.in/en/daily-programme). The temple closing time is not listed in the records we have. | medium | Shej (night) aarti is held at 10:00 PM (source: https://sai.org.in/en/daily-programme). The temple closing time is not listed in the records I have. | medium |

## My conclusion (write 4 to 5 lines in your own words)

- Which version gave more correct, grounded answers? ...
- Which version was more honest on Q6 (the question the data cannot answer)? ...
- Which version gave better follow-up questions? ...
- Which prompt will I keep, and why? ...
- One thing I would improve next: ...

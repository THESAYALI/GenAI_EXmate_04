A pilgrim asked this question:
"""{question}"""

CONTEXT_RECORDS (from the official Sansthan website):
{context}

Follow these steps silently, then give only the final JSON:
STEP 1. Read every record. Decide: does any record DIRECTLY answer the question?
STEP 2. If yes: give the exact timing or price from the record, with its unit (for example "INR" or the hours), name the place_or_service, and add the source_url. Confidence is "high".
STEP 3. If the records answer only part of it: give that part, say what is missing, confidence is "medium".
STEP 4. If no record answers it (or the question needs live information such as queue, crowd, availability now): do NOT use a nearby record as a substitute. Say you do not have that information, confidence is "low".
STEP 5. Write one follow_up that helps a family planning a trip (for example ask the number of people, the travel day, or suggest the official website when data is missing).

EXAMPLES OF THE FORMAT (the facts below are made up only to show the shape):
Example A (answer found)
Records: [{"topic": "Example Hall", "timing": "10:00 AM to 11:00 AM", "source_url": "https://example.org/a"}]
Question: When is Example Hall open?
JSON: {"answer": "Example Hall is open from 10:00 AM to 11:00 AM (source: https://example.org/a).", "confidence": "high", "follow_up": "Which day are you planning to visit?"}

Example B (answer not in records)
Records: [{"topic": "Example Hall", "timing": "10:00 AM to 11:00 AM", "source_url": "https://example.org/a"}]
Question: How many people are inside Example Hall right now?
JSON: {"answer": "I don't have live crowd information in my data, so I cannot tell how many people are inside right now.", "confidence": "low", "follow_up": "You can ask at the Sansthan office or check https://sai.org.in for official updates."}

Now reply with ONE JSON object only: {"answer": "...", "confidence": "high|medium|low", "follow_up": "..."}

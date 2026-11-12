"""Static ShirdiYatra knowledge base.

This is the ONLY data the assistant can answer from. It is a small, hand-written
sample: always verify timings and booking rules with the official Shri Saibaba
Sansthan Trust (sai.org.in) before travelling.

Each fact has:
  id        - short unique name
  keywords  - lowercase words that signal this fact is relevant
  answer    - the text returned to the user
"""

FACTS = [
    {
        "id": "aarti_timings",
        "keywords": ["aarti", "kakad", "madhyahna", "dhoop", "shej", "morning", "evening", "noon"],
        "answer": (
            "Four aartis are held daily: Kakad (early morning, around 5:15 AM), "
            "Madhyahna (noon, around 12:00 PM), Dhoop (sunset, around 6:30 PM) and "
            "Shej (night, around 10:30 PM). Exact times shift slightly by season."
        ),
    },
    {
        "id": "darshan_timings",
        "keywords": ["darshan", "timings", "open", "close", "opening", "closing", "hours", "mandir"],
        "answer": (
            "The Samadhi Mandir is generally open from about 4:00 AM to 10:30 PM. "
            "It is closed to regular darshan for a short time during each aarti."
        ),
    },
    {
        "id": "pune_to_shirdi",
        "keywords": ["pune", "reach", "travel", "road", "drive", "bus", "cab", "distance"],
        "answer": (
            "Shirdi is roughly 185 km from Pune. The usual way is by road (about 4-5 hours "
            "by car or bus) via the Pune-Ahmednagar-Shirdi route."
        ),
    },
    {
        "id": "stay",
        "keywords": ["stay", "accommodation", "hotel", "room", "lodging", "dharamshala", "bhaktaniwas"],
        "answer": (
            "You can stay at Sansthan-run Bhaktaniwas / Dwarawati-type guest houses, or at "
            "private hotels and dharamshalas in Shirdi town. Book ahead during festivals "
            "such as Ram Navami and Guru Purnima."
        ),
    },
    {
        "id": "nearest_station_airport",
        "keywords": ["railway", "station", "train", "airport", "flight", "nearest", "fly"],
        "answer": (
            "The railway station is Sainagar Shirdi. Shirdi also has its own airport "
            "(Shirdi / Sai Baba Airport), a few km outside the town."
        ),
    },
    {
        "id": "nearby_places",
        "keywords": ["nearby", "places", "visit", "dwarkamai", "chavadi", "lendi", "shani", "shingnapur"],
        "answer": (
            "Inside Shirdi: Dwarkamai, Chavadi and Lendi Baug. Within a day trip: "
            "Shani Shingnapur (about 70 km) and Nashik / Trimbakeshwar."
        ),
    },
    {
        "id": "dress_code",
        "keywords": ["dress", "clothes", "wear", "attire", "code"],
        "answer": (
            "There is no strict dress code, but modest, comfortable clothing is "
            "recommended. Shoes, bags and phones usually go in the cloakroom/locker "
            "before entering the temple."
        ),
    },
    {
        "id": "online_booking",
        "keywords": ["book", "booking", "online", "pass", "ticket", "reservation", "register"],
        "answer": (
            "Darshan and aarti passes can be booked on the official Sansthan website "
            "(sai.org.in). Use only the official site to avoid fake booking portals."
        ),
    },
    {
        "id": "food",
        "keywords": ["food", "meal", "prasad", "prasadalaya", "lunch", "dinner", "eat"],
        "answer": (
            "Sai Prasadalaya serves subsidised meals to devotees (lunch and dinner), "
            "usually through a coupon system."
        ),
    },
]

# ShirdiYatra

**Course:** Sanjivani SJ-50 | **Domain:** Travel & Culture
**Student:** Sayali Rajendra Pawar (CSE, SJ-50)

## Project Card

### Product
ShirdiYatra is a command-line trip planner for a visit to Shirdi. It answers questions about Sai Baba Sansthan's daily programme (aarti and darshan timings) and Sansthan accommodation (room types and tariffs). It also gives simple rule-based tips for pilgrims.

### User
A family of 7 from Hyderabad, including grandparents, making their first 2-day trip to Shirdi. They travel by train to Kopargaon and want affordable Sansthan rooms that suit a group.

### Problem
Shirdi information is scattered across many web pages. Families struggle to find:
- aarti and darshan timings, so they can plan the day around them
- which Sansthan rooms fit a large group and a budget
- how to reach Shirdi and what rules or tips to follow

Wrong or old information can mean missed aartis or the wrong room booking.

### Data Source
Official Shri Sai Baba Sansthan Trust website only:
- https://sai.org.in/en/faq
- https://sai.org.in/en/daily-programme

Each record stores: `topic`, `place_or_service`, `timing`, `cost_inr`, `rule_or_tip`, `source_url`, plus a "checked on" date.

## Day 01 Files

| File | Purpose |
|------|---------|
| `day01/day01_intro.py` | Prints the project card using variables and f-strings, then asks the user's name and question with `input()` |
| `day01/day01_menu.py` | `while` loop menu: 1 = about ShirdiYatra, 2 = sample questions, 3 = rule check with `if/elif`, 0 = exit |

## How to Run

```bash
python day01/day01_intro.py
python day01/day01_menu.py
```

## Planned Wow Feature
A one-day Shirdi timeline card with the train arrival marked, and a `plan_sansthan_rooms` tool that suggests the cheapest room mix for the group.
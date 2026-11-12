# Day 1 - Project Card, Intro Script and Menu

**Project:** ShirdiYatra | **Track:** Travel & culture | **Day:** D1 (Wed 4 Nov)

This README explains everything done on Day 1: what the task asked, which file does each part, how each file works line by line, and what every Python term used means.

---

## 1. The Day 1 task (from the task sheet)

> Create a public repo and clone it. `README.md` = your project card (product, user, problem, data source). `day01_intro.py` prints the card with variables + f-strings and asks the user's name and question with `input()`. `day01_menu.py`: while-loop menu (1 about, 2 sample questions, 3 one if/elif rule check from your domain, 0 exit). Push.

The sheet's example repo name is `sanjivani-sj-01-canemitra`. For this project the matching repo is `GenAI_EXmate_04` (your project row also lists `sanjivani-sj-50-shirdiyatra`).

## 2. Task checklist and where each file is

| # | Task point | File | Where it is | Status |
|---|---|---|---|---|
| 1 | Create a public repo and clone it | GitHub repo `GenAI_EXmate_04` | github.com/THESAYALI/GenAI_EXmate_04 | Done (cloned to your PC) |
| 2 | `README.md` = project card (product, user, problem, data source) | `README.md` | **Project root** (one level above this folder): `../README.md` | Done |
| 3 | `day01_intro.py`: card with variables + f-strings, asks name and question with `input()` | `day01_intro.py` | This folder: `day01/day01_intro.py` | Done |
| 4 | `day01_menu.py`: while-loop menu (1, 2, 3, 0) | `day01_menu.py` | This folder: `day01/day01_menu.py` | Done |
| 5 | Push | Git commands | See section 9 | Do it from your PC |

### Folder layout for Day 1

```
GenAI_EXmate_04/
├── README.md               <- the project card (root, not inside day01)
└── day01/
    ├── README.md           <- this file (explains Day 1)
    ├── day01_intro.py      <- prints the card, asks name + question
    └── day01_menu.py       <- while-loop menu
```

Later days put their code in `app/`, `data/` and `analysis/`. Day 1 has no code in `app/`; everything is inside `day01/`.

---

## 3. The project card (root `README.md`)

A **project card** is a short summary of your project. It answers four questions:

| Part | Meaning | ShirdiYatra answer |
|---|---|---|
| **Product** | What the thing is and does | Plans a Shirdi visit from the Sansthan's own pages: aarti and darshan timings, which Sansthan rooms fit your group and budget, and how to reach |
| **User** | Who will use it | A family of 7 from Hyderabad (grandparents included) planning their first 2-day Shirdi trip by train to Kopargaon, who want Sansthan rooms, not costly hotels |
| **Problem** | What is hard today | Prices and rules change and appear in several versions (English, Hindi, Marathi, old mirror copies), and fake look-alike websites exist |
| **Data source** | Where the facts come from | Official Sansthan pages: `sai.org.in/en/faq`, `sai.org.in/en/daily-programme` |

**Why a README?** `README.md` is the first file GitHub shows on the repo page. The `.md` ending means **Markdown**, a simple text format where `#` makes a heading, `|` makes a table and `**text**` makes bold.

---

## 4. `day01_intro.py` explained

**What it does:** prints the project card using variables, then asks for the user's name and question and replies.

### Code walkthrough

| Lines | Code | What it does |
|---|---|---|
| 1 | `# Day 1 - ...` | A **comment**. Python ignores it; it is a note for humans |
| 3-14 | `project = "ShirdiYatra"` etc. | **Variables** holding text (strings) for the card: `project`, `track`, `product`, `user`, `problem`, `data_source` |
| 5-7 | `product = ("..." "..." "...")` | One long string written on several lines inside `( )`. Python joins the pieces into one string |
| 16 | `print("=" * 60)` | Prints a line of 60 `=` signs. `"=" * 60` repeats the text 60 times |
| 17 | `print(f"  {project}  ({track})")` | An **f-string**: `{project}` is replaced by the variable's value |
| 19-22 | `print(f"Product     : {product}")` | Prints each card field with a label |
| 25 | `name = input("Your name: ").strip()` | Asks the user to type their name and stores it |
| 26 | `question = input("Your question about Shirdi: ").strip()` | Asks for their question |
| 29 | `print(f"Sai Ram {name}!")` | Greets the user using what they typed |
| 30 | `print(f"You asked: \"{question}\"")` | Repeats the question. `\"` prints a quote mark inside a string |
| 31 | `print(f"{project} will answer ...")` | Tells the user the answer will come from official pages once data is loaded |

### Example run

```
============================================================
  ShirdiYatra  (Travel & culture)
============================================================
Product     : Plans a Shirdi visit from the Sansthan's own pages: ...
User        : A family of 7 from Hyderabad ...
Problem     : Prices and rules change ...
Data source : https://sai.org.in/en/faq and https://sai.org.in/en/daily-programme
============================================================
Your name: Yash
Your question about Shirdi: When is Shej aarti?

Sai Ram Yash!
You asked: "When is Shej aarti?"
ShirdiYatra will answer this from official Sansthan pages once the data is loaded.
```

---

## 5. `day01_menu.py` explained

**What it does:** shows a numbered menu again and again until the user chooses `0`.

| Choice | What happens | Python idea used |
|---|---|---|
| `1` | Shows what ShirdiYatra is | function `show_about()` |
| `2` | Lists the 6 sample questions | list + `for` loop + `enumerate` |
| `3` | Room rule check (domain rule) | `input`, `int`, `try/except`, `if/elif/else` |
| `0` | Says goodbye and stops | `break` |
| anything else | "Invalid choice" | the final `else` |

### Code walkthrough

| Part | What it does |
|---|---|
| `SAMPLE_QUESTIONS = [ ... ]` | A **list** of 6 strings (the 6 sample questions from the project row). The name is in CAPITALS because it is a **constant**, a value that should not change |
| `def show_about():` | A **function** that prints a short description of the project |
| `def show_questions():` | A function that prints every question with a number. `enumerate(SAMPLE_QUESTIONS, start=1)` gives each question its number starting from 1 |
| `def rule_check():` | A function for the **room rule check** (see below) |
| `def main():` | The function that holds the menu loop |
| `while True:` | The **while loop**: repeats forever until `break` |
| `choice = input("Choose: ").strip()` | Reads the user's menu choice |
| `if / elif / else` | Picks what to do for `"1"`, `"2"`, `"3"`, `"0"` or anything else |
| `break` | Leaves the `while` loop, so the program ends |
| `main()` (last line) | Starts the program |

### The domain rule check (menu option 3)

The rule check uses two real Sansthan rules from your project row: **no single-person rooms** and **stay must be 24 to 48 hours**.

```python
if people < 1:
    print("Group size must be at least 1.")
elif people == 1:
    print("Not allowed: Sansthan does not give single-person rooms.")
elif hours < 24:
    print("... below the 24-hour minimum.")
elif hours > 48:
    print("... above the 48-hour maximum.")
else:
    print("OK: ... fits the room rules.")
```

Python checks these top to bottom and runs **only the first one that is true**.

| People | Hours | Result |
|---|---|---|
| 1 | 30 | Not allowed (single-person room) |
| 7 | 10 | Below the 24-hour minimum |
| 7 | 60 | Above the 48-hour maximum |
| 7 | 40 | OK |
| abc | 40 | "Please enter whole numbers." |

The `try/except ValueError` part catches the case where the user types letters instead of a number, so the program does not crash.

### Example run

```
--- ShirdiYatra Menu ---
1. About ShirdiYatra
2. Sample questions
3. Room rule check
0. Exit
Choose: 3

Sansthan room rule check
Number of people travelling: 7
Planned stay in hours: 40
OK: 7 people for 40 h fits the room rules.
```

---

## 6. Glossary: every term used on Day 1

### Python basics

| Term | Meaning | Example in this project |
|---|---|---|
| **Script** | A `.py` file you run with `python filename.py` | `day01_intro.py` |
| **Comment** | A line starting with `#`; Python ignores it | `# Day 1 - ShirdiYatra menu` |
| **Variable** | A name that stores a value | `project = "ShirdiYatra"` |
| **String (`str`)** | Text inside quotes | `"Travel & culture"` |
| **Integer (`int`)** | A whole number | `24`, `48`, `7` |
| **List** | An ordered collection in `[ ]` | `SAMPLE_QUESTIONS` |
| **Constant** | A variable you do not plan to change; written in CAPITALS by habit | `SAMPLE_QUESTIONS` |
| **`print()`** | Shows text on the screen | `print("Hello")` |
| **`input()`** | Waits for the user to type and returns what they typed as a string | `name = input("Your name: ")` |
| **`.strip()`** | Removes extra spaces at the start and end of a string | `"  Yash ".strip()` gives `"Yash"` |
| **`int()`** | Converts text to a whole number | `int("7")` gives `7` |
| **f-string** | A string starting with `f` where `{name}` is replaced by the variable's value | `f"Sai Ram {name}!"` |
| **Escape `\"`** | Puts a quote mark inside a string | `f"You asked: \"{question}\""` |
| **String repeat `*`** | Repeats a string | `"=" * 60` |

### Control flow

| Term | Meaning | Example |
|---|---|---|
| **`if`** | Runs code only when a condition is true | `if people == 1:` |
| **`elif`** | "else if": checked only if earlier conditions were false | `elif hours < 24:` |
| **`else`** | Runs when none of the above matched | `else: print("Invalid choice")` |
| **Condition** | Something that is `True` or `False` | `hours > 48` |
| **Comparison operators** | `==` equal, `<` less than, `>` greater than | `people == 1` |
| **`while` loop** | Repeats while a condition is true | `while True:` |
| **`break`** | Stops the loop immediately | used for choice `0` |
| **`for` loop** | Repeats once for each item in a list | loop over `SAMPLE_QUESTIONS` |
| **`enumerate()`** | Gives (number, item) pairs while looping | numbers the questions 1 to 6 |
| **Indentation** | The spaces at the start of a line show which code belongs inside the `if`, `while` or `def` | 4 spaces |

### Functions and errors

| Term | Meaning | Example |
|---|---|---|
| **Function (`def`)** | A named block of code you can run by calling its name | `def show_about():` |
| **Call a function** | Running it by writing its name and `( )` | `show_about()` |
| **`return`** | Leaves a function early (here an empty `return` after bad input) | in `rule_check()` |
| **`try` / `except`** | Tries code; if an error happens, runs the `except` part instead of crashing | `except ValueError:` |
| **`ValueError`** | The error Python raises when `int("abc")` cannot convert | caught in `rule_check()` |

### Project and Git words

| Term | Meaning |
|---|---|
| **Repo (repository)** | A project folder tracked by Git and stored on GitHub |
| **Public repo** | Anyone can view it on GitHub |
| **Clone** | Download a copy of a GitHub repo to your computer with `git clone <url>` |
| **Commit** | A saved snapshot of your changes with a message |
| **Push** | Upload your commits to GitHub with `git push` |
| **Project card** | A short README summary of product, user, problem and data source |
| **Markdown (`.md`)** | The text format README files use |
| **Domain** | The area your project is about; here, Shirdi travel (rooms, aartis, darshan) |
| **Rule check** | A small piece of code that tests a real rule from your domain |
| **Sansthan** | Shri Saibaba Sansthan Trust, which runs the temple and rooms in Shirdi |
| **Aarti** | A prayer ritual with set times (Kakad, Mid-day, Dhoop, Shej) |
| **Darshan** | Seeing the deity; people wait in a queue for it |

---

## 7. How to run Day 1

Open a terminal in the **project root** (the folder that contains `day01`, `app`, `README.md`):

```
python day01/day01_intro.py
python day01/day01_menu.py
```

If `python` is not found on Windows, use `py day01/day01_intro.py`.

## 8. Questions you may be asked (with short answers)

| Question | Answer |
|---|---|
| What is an f-string? | A string with `f` in front where `{variable}` is replaced by its value |
| What does `input()` return? | Always text (a string), even if the user types a number |
| Why use `int()`? | To turn the typed text into a number so it can be compared with `<` and `>` |
| Why `while True`? | So the menu repeats until the user chooses `0`, which runs `break` |
| What is the difference between `if` and `elif`? | `elif` is only checked when the earlier `if` was false |
| Why `try/except`? | So typing letters instead of a number does not crash the program |
| What is the domain rule? | No single-person rooms; stay of 24 to 48 hours |
| Where is the project card? | Root `README.md` |

## 9. Push Day 1 to GitHub

```
git add .
git commit -m "Day 1: project card, intro and menu"
git push origin main
```

## 10. Day 1 status

| Item | Status |
|---|---|
| Public repo created and cloned | Done |
| Project card (`../README.md`) | Done |
| `day01_intro.py` | Done and tested |
| `day01_menu.py` | Done and tested |
| Push | Done when `git push` succeeds (check github.com/THESAYALI/GenAI_EXmate_04) |

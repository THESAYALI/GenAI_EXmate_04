# Day 1 - ShirdiYatra menu (while loop + if/elif)

SAMPLE_QUESTIONS = [
    "What time is the Shej aarti and the Kakad aarti in Shirdi?",
    "How far is Shirdi from Kopargaon railway station and the airport?",
    "Can I get a Sansthan room if I am travelling alone?",
    "We are 7 people for 1 night, non-AC is fine. Which Sansthan rooms "
    "should we book and what will it cost?",
    "We reach Kopargaon at 11 am on Thursday. Which aartis can we attend "
    "that day and the next morning before our 2 pm train?",
    "How long is the darshan queue on Guru Purnima this year?",
]


def show_about():
    print("\nShirdiYatra plans a Shirdi visit from the Sansthan's own pages:")
    print("aarti and darshan timings, Sansthan rooms for your group and budget,")
    print("and how to reach. Built for a family of 7 on a first 2-day trip.")
    print("Data: https://sai.org.in/en/faq , https://sai.org.in/en/daily-programme")


def show_questions():
    print("\nSample questions:")
    for number, q in enumerate(SAMPLE_QUESTIONS, start=1):
        print(f"  {number}) {q}")


def rule_check():
    # Domain rule: no single-person rooms; stay must be 24-48 hours.
    print("\nSansthan room rule check")
    try:
        people = int(input("Number of people travelling: "))
        hours = int(input("Planned stay in hours: "))
    except ValueError:
        print("Please enter whole numbers.")
        return

    if people < 1:
        print("Group size must be at least 1.")
    elif people == 1:
        print("Not allowed: Sansthan does not give single-person rooms.")
    elif hours < 24:
        print(f"Stay of {hours} h is below the 24-hour minimum.")
    elif hours > 48:
        print(f"Stay of {hours} h is above the 48-hour maximum.")
    else:
        print(f"OK: {people} people for {hours} h fits the room rules.")


def main():
    while True:
        print("\n--- ShirdiYatra Menu ---")
        print("1. About ShirdiYatra")
        print("2. Sample questions")
        print("3. Room rule check")
        print("0. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            show_about()
        elif choice == "2":
            show_questions()
        elif choice == "3":
            rule_check()
        elif choice == "0":
            print("Sai Ram! Goodbye.")
            break
        else:
            print("Invalid choice, try 0-3.")


main()

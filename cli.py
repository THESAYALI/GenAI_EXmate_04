# app/cli.py
# Day 2: menu for ShirdiYatra (uses a while loop)
# Author: Sayali Rajendra Pawar | CSE | SJ-50

from app import records as db


def show(items):
    """Print a list of records neatly."""
    if not items:
        print("No records found.")
        return
    for i, r in enumerate(items, start=1):
        cost = "-" if r["cost_inr"] is None else f"Rs {r['cost_inr']}"
        print(f"{i}. [{r['topic']}] {r['place_or_service']} | {r['timing']} | {cost}")
        print(f"     {r['rule_or_tip']}")


def main():
    print("=== ShirdiYatra ===")
    name = input("Enter your name: ")
    print(f"Sai Ram {name}!")
    data = db.load_records()

    while True:
        print("\n1. View all records")
        print("2. Search")
        print("3. Show Daily programme")
        print("4. Show Accommodation")
        print("5. Add a record")
        print("6. Delete a record")
        print("0. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            show(data)
        elif choice == "2":
            show(db.search_records(data, input("Keyword: ")))
        elif choice == "3":
            show(db.filter_by_topic(data, "Daily programme"))
        elif choice == "4":
            show(db.filter_by_topic(data, "Accommodation"))
        elif choice == "5":
            topic = input("Topic (Daily programme / Accommodation): ")
            place = input("Place or service: ")
            timing = input("Timing: ")
            cost = input("Cost in Rs (press Enter if none): ")
            tip = input("Rule or tip: ")
            db.add_record(data, topic, place, timing, int(cost) if cost else None, tip)
            print("Record added.")
        elif choice == "6":
            show(data)
            num = int(input("Number to delete: "))
            removed = db.delete_record(data, num)
            print("Deleted:", removed["place_or_service"] if removed else "Invalid number.")
        elif choice == "0":
            print("Sai Ram! Have a safe yatra.")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
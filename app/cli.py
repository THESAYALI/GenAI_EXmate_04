from app.records import load_records, search, count_by, get_by_id

records = load_records()

while True:
    print("\n1. Search  2. Count by field  3. Get by ID  4. Exit")
    choice = input("Choose: ").strip()
    if choice == "1":
        for r in search(records, input("Keyword: ")):
            print(r["topic"], "-", r["place_or_service"])
    elif choice == "2":
        print(count_by(records, input("Field (e.g. topic): ")))
    elif choice == "3":
        print(get_by_id(records, input("ID: ")) or "Not found")
    elif choice == "4":
        break
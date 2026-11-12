# Day 1 - ShirdiYatra project card with variables, f-strings and input()

project = "ShirdiYatra"
track = "Travel & culture"
product = ("Plans a Shirdi visit from the Sansthan's own pages: aarti and "
           "darshan timings, which Sansthan rooms fit your group and budget, "
           "and how to reach.")
user = ("A family of 7 from Hyderabad (grandparents included) planning their "
        "first 2-day Shirdi trip by train to Kopargaon, who want to stay in "
        "Sansthan rooms, not costly hotels.")
problem = ("Prices and rules change and appear in several versions (English, "
           "Hindi, Marathi, older mirror copies), and fake look-alike "
           "websites exist.")
data_source = "https://sai.org.in/en/faq and https://sai.org.in/en/daily-programme"

print("=" * 60)
print(f"  {project}  ({track})")
print("=" * 60)
print(f"Product     : {product}")
print(f"User        : {user}")
print(f"Problem     : {problem}")
print(f"Data source : {data_source}")
print("=" * 60)

name = input("Your name: ").strip()
question = input("Your question about Shirdi: ").strip()

print()
print(f"Sai Ram {name}!")
print(f"You asked: \"{question}\"")
print(f"{project} will answer this from official Sansthan pages once the data is loaded.")

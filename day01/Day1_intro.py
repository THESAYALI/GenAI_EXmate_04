# day01_intro.py
# Day 1: ShirdiYatra intro
# Author: Sayali Rajendra Pawar | CSE | SJ-50

product = "ShirdiYatra"
target_user = "Families visiting Shirdi for the first time, travelling by train to Kopargaon"
problem = "Aarti timings, rooms and travel details are spread over many pages, and fake websites cause confusion."
solution = "A simple Shirdi trip planning assistant."
data_source = "Shree Saibaba Sansthan Trust, Shirdi (sai.org.in)"

print(f"Product: {product}")
print(f"User: {target_user}")
print(f"Problem: {problem}")
print(f"Solution: {solution}")
print(f"Data Source: {data_source}")

name = input("Enter your name: ")
place = input("Distance from Shirdi to (airport / kopargaon / sainagar)? ").lower()

print(f"Sai Ram {name}!")

if place == "airport":
    print("Shirdi airport is 17 km from Shirdi.")
elif place == "kopargaon":
    print("Kopargaon railway station is 17 km from Shirdi.")
elif place == "sainagar":
    print("Sainagar Shirdi railway station is 4 km from Shirdi.")
else:
    print("Sorry, I don't have that place yet.")
"""fetch.py - download official Sai Sansthan pages and save the HTML in data/raw/."""
import os
import urllib.request
from datetime import date

RAW_DIR = os.path.join("data", "raw")

PAGES = {
    "1": ("faq", "https://www.sai.org.in/en/faq"),
    "2": ("daily-programme", "https://www.sai.org.in/en/daily-programme"),
}


def fetch_page(name, url):
    """Download one page, save it, return the saved path."""
    os.makedirs(RAW_DIR, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    path = os.path.join(RAW_DIR, f"{name}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path


def main():
    print("Fetch official pages")
    for key, (name, url) in PAGES.items():
        print(f"  {key}. {name}  ({url})")
    print("  3. all")
    choice = input("Choose: ").strip()

    if choice == "3":
        todo = list(PAGES.values())
    elif choice in PAGES:
        todo = [PAGES[choice]]
    else:
        print("Invalid choice.")
        return

    for name, url in todo:
        try:
            path = fetch_page(name, url)
            print(f"Saved {path} (checked on {date.today()})")
        except Exception as e:
            print(f"Could not fetch {url}: {e}")


if __name__ == "__main__":
    main()

"""app/fetch.py - download official Sai Sansthan pages into data/raw/ (Day 3).

Run from the project root:
    python -m app.fetch

Saves each page as data/raw/<name>.html and writes data/raw/manifest.json
(url, status, size, date) so app/ingest.py can store a 'checked on' date.
"""
import json
import os
import sys
from datetime import date
from urllib.parse import urlparse

import requests

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
MANIFEST = os.path.join(RAW_DIR, "manifest.json")
OFFICIAL_DOMAIN = "sai.org.in"
TIMEOUT = (5, 20)   # (connect seconds, read seconds)
HEADERS = {"User-Agent": "Mozilla/5.0 (ShirdiYatra student project)"}

PAGES = {
    "faq": "https://sai.org.in/en/faq",
    "daily-programme": "https://sai.org.in/en/daily-programme",
    "accomodations": "https://sai.org.in/en/accomodations",   # the site spells it this way
    "how-to-reach-shirdi": "https://sai.org.in/en/how-to-reach-shirdi",
}


def is_official(url):
    host = urlparse(url).netloc.lower()
    return host == OFFICIAL_DOMAIN or host.endswith("." + OFFICIAL_DOMAIN)


def fetch_page(name, url):
    """Download one page and save it. Returns a manifest entry (never raises)."""
    entry = {"name": name, "url": url, "fetched_on": str(date.today()),
             "ok": False, "bytes": 0, "error": None}
    if not is_official(url):
        entry["error"] = "not an official sai.org.in URL"
        return entry
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        os.makedirs(RAW_DIR, exist_ok=True)
        path = os.path.join(RAW_DIR, f"{name}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(resp.text)
        entry.update(ok=True, bytes=len(resp.content))
    except requests.exceptions.Timeout:
        entry["error"] = "timed out"
    except requests.exceptions.HTTPError as e:
        entry["error"] = f"HTTP {e.response.status_code}"
    except requests.exceptions.RequestException as e:
        entry["error"] = f"{type(e).__name__}: {e}"
    except OSError as e:
        entry["error"] = f"could not save file: {e}"
    return entry


def fetch_all(pages=None):
    entries = [fetch_page(name, url) for name, url in (pages or PAGES).items()]
    os.makedirs(RAW_DIR, exist_ok=True)
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
    return entries


def main():
    entries = fetch_all()
    for e in entries:
        status = f"saved ({e['bytes']} bytes)" if e["ok"] else f"FAILED - {e['error']}"
        print(f"{e['name']:<22} {status}")
    ok = sum(e["ok"] for e in entries)
    print(f"\n{ok}/{len(entries)} pages saved in data/raw/ on {date.today()}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

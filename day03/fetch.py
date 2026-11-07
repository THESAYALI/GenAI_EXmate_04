"""S2: download official Sansthan pages into data/raw/."""
import json
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

SOURCES = {
    "faq": "https://sai.org.in/en/faq",
    "daily_programme": "https://sai.org.in/en/daily-programme",
    "how_to_reach": "https://sai.org.in/en/how-to-reach-shirdi",
    "accommodations": "https://sai.org.in/en/accomodations",
}

ALLOWED_DOMAIN = "sai.org.in"
HEADERS = {"User-Agent": "Mozilla/5.0 (ShirdiYatra student project)"}
TIMEOUT = (5, 15)  # (connect seconds, read seconds)
RETRIES = 3


def download(name: str, url: str, session: requests.Session) -> dict:
    """Download one page. Never raises; returns a result dict."""
    if urlparse(url).netloc != ALLOWED_DOMAIN:
        return {"name": name, "url": url, "ok": False,
                "error": "domain not allowed"}

    last_error = "unknown error"
    for attempt in range(1, RETRIES + 1):
        try:
            resp = session.get(url, headers=HEADERS, timeout=TIMEOUT)
            resp.raise_for_status()
            html = resp.content.decode("utf-8", errors="replace")
            if not html.strip():
                raise ValueError("empty response")
            path = RAW_DIR / f"{name}.html"
            path.write_text(html, encoding="utf-8")
            return {"name": name, "url": url, "ok": True,
                    "file": path.name, "bytes": len(html),
                    "fetched_on": date.today().isoformat()}
        except requests.exceptions.Timeout:
            last_error = "timeout"
        except requests.exceptions.HTTPError as e:
            last_error = f"http error {e.response.status_code}"
            if e.response.status_code < 500:
                break  # 4xx will not fix itself, do not retry
        except requests.exceptions.ConnectionError:
            last_error = "connection error"
        except (requests.exceptions.RequestException, OSError, ValueError) as e:
            last_error = str(e)
        print(f"  attempt {attempt}/{RETRIES} failed for {name}: {last_error}")
        time.sleep(attempt)

    return {"name": name, "url": url, "ok": False, "error": last_error}


def fetch_all() -> list:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    with requests.Session() as session:
        for name, url in SOURCES.items():
            print(f"Downloading {name} ...")
            results.append(download(name, url, session))

    manifest = {r["name"]: r for r in results}
    (RAW_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return results


if __name__ == "__main__":
    results = fetch_all()
    ok = [r for r in results if r["ok"]]
    print(f"\nDownloaded {len(ok)}/{len(results)} documents")
    for r in results:
        status = f"OK ({r['bytes']} bytes)" if r["ok"] else f"FAILED ({r['error']})"
        print(f"  {r['name']}: {status}")
    sys.exit(0 if len(ok) >= 3 else 1)
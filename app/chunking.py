"""
app/chunking.py  --  D7 / S1
Split ShirdiYatra documents into small searchable chunks.
Every chunk keeps: source (URL or file), page (section number inside the source) and title.

Documents are read from:
  1. data/records.json (or data/sample_records.json)  -> one document per record
  2. data/raw/*.html, *.htm, *.txt, *.md              -> pages downloaded by app/fetch.py

Run directly to preview:  python -m app.chunking
"""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"

# file-name keyword -> official source URL (edit if your fetch.py saves other names)
KNOWN_SOURCES = {
    "faq": "https://sai.org.in/en/faq",
    "daily": "https://sai.org.in/en/daily-programme",
    "reach": "https://sai.org.in/en/how-to-reach-shirdi",
    "accomodation": "https://sai.org.in/en/accomodations",
    "accommodation": "https://sai.org.in/en/accomodations",
}

MAX_CHARS = 600        # target size of one chunk
OVERLAP_SENTENCES = 1  # sentences repeated between neighbouring chunks


# ---------------------------------------------------------------- HTML -> sections
class _SectionParser(HTMLParser):
    """Turns an HTML page into a title + list of (heading, text) sections."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.sections = []          # [{"heading": str, "lines": [str]}]
        self._skip = 0
        self._in_title = False
        self._in_heading = False
        self._buf = []
        self._new_section("Introduction")

    def _new_section(self, heading):
        self.sections.append({"heading": heading, "lines": []})

    def _flush(self):
        text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
        self._buf = []
        if text:
            self.sections[-1]["lines"].append(text)

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "nav", "footer", "noscript"):
            self._skip += 1
        elif tag == "title":
            self._in_title = True
        elif tag in ("h1", "h2", "h3"):
            self._flush()
            self._in_heading = True
        elif tag in ("td", "th"):
            self._buf.append(" | ")
        elif tag in ("p", "li", "br", "tr", "div"):
            self._flush()

    def handle_endtag(self, tag):
        if tag in ("script", "style", "nav", "footer", "noscript"):
            self._skip = max(0, self._skip - 1)
        elif tag == "title":
            self._in_title = False
        elif tag in ("h1", "h2", "h3"):
            heading = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            self._buf = []
            self._in_heading = False
            if heading:
                self._new_section(heading)
        elif tag in ("p", "li", "tr", "div"):
            self._flush()

    def handle_data(self, data):
        if self._skip:
            return
        if self._in_title:
            self.title += data
        else:
            self._buf.append(data)

    def close(self):
        super().close()
        self._flush()


def parse_html(html):
    p = _SectionParser()
    p.feed(html)
    p.close()
    title = re.sub(r"\s+", " ", p.title).strip()
    sections = [(s["heading"], "\n".join(s["lines"])) for s in p.sections if s["lines"]]
    return title, sections


# ---------------------------------------------------------------- text -> chunks
def split_text(text, max_chars=MAX_CHARS, overlap=OVERLAP_SENTENCES):
    """Sentence-aware splitting with a small overlap, so facts are not cut in half."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]
    chunks, current = [], []
    for sent in sentences:
        if current and len(" ".join(current + [sent])) > max_chars:
            chunks.append(" ".join(current))
            current = current[-overlap:] if overlap else []
        current.append(sent)
    if current:
        chunks.append(" ".join(current))
    return chunks


def _make_chunks(doc_id, text, source, page, title):
    out = []
    for i, piece in enumerate(split_text(text)):
        out.append({
            "id": f"{doc_id}-p{page}-c{i}",
            "text": piece,
            "source": source,
            "page": page,
            "title": title,
            "chunk_index": i,
        })
    return out


def _source_for(path):
    name = path.stem.lower()
    for key, url in KNOWN_SOURCES.items():
        if key in name:
            return url
    return path.name


# ---------------------------------------------------------------- loaders
def chunks_from_records():
    for name in ("records.json", "sample_records.json"):
        f = ROOT / "data" / name
        if f.exists():
            records = json.loads(f.read_text(encoding="utf-8"))
            break
    else:
        return []
    if isinstance(records, dict):
        records = records.get("records", [])
    out = []
    for n, r in enumerate(records, start=1):
        title = f"{r.get('topic', 'record')} - {r.get('place_or_service', '')}".strip(" -")
        parts = [
            f"{r.get('topic', '')}: {r.get('place_or_service', '')}.",
            f"Timing: {r['timing']}." if r.get("timing") else "",
            f"Cost: Rs {r['cost_inr']}." if r.get("cost_inr") not in (None, "") else "",
            f"Tip: {r['rule_or_tip']}." if r.get("rule_or_tip") else "",
            f"Checked on {r['checked_on']}." if r.get("checked_on") else "",
        ]
        text = " ".join(p for p in parts if p)
        source = r.get("source_url") or f"{f.name}#{n}"
        out += _make_chunks(f"rec{r.get('id', n)}", text, source, 1, title)
    return out


def chunks_from_raw():
    out = []
    if not RAW_DIR.exists():
        return out
    for path in sorted(RAW_DIR.iterdir()):
        if path.suffix.lower() not in (".html", ".htm", ".txt", ".md"):
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        source = _source_for(path)
        if path.suffix.lower() in (".html", ".htm"):
            title, sections = parse_html(content)
            title = title or path.stem
        else:
            title = path.stem
            sections = [(f"Part {i + 1}", block) for i, block in
                        enumerate(re.split(r"\n\s*\n", content)) if block.strip()]
        for page, (heading, text) in enumerate(sections, start=1):
            out += _make_chunks(path.stem, text, source, page, f"{title} - {heading}")
    return out


def load_all_chunks():
    return chunks_from_records() + chunks_from_raw()


if __name__ == "__main__":
    chunks = load_all_chunks()
    print(f"{len(chunks)} chunks")
    for c in chunks[:5]:
        print(f"- [{c['id']}] {c['title']} | page {c['page']} | {c['source']}\n    {c['text'][:110]}...")

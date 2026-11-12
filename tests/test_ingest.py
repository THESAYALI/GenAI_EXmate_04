"""Tests for app/ingest.py using small HTML snippets shaped like the Sansthan pages.

These are hand-written fixtures, not downloads. Run the real check yourself with
    python -m app.fetch && python -m app.ingest
Run these with:  python -m pytest tests
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ingest import is_official, parse_faq, parse_programme, parse_rooms

URL = "https://sai.org.in/en/x"

PROGRAMME = """
<ul>
<li><img src="a.svg">Temple Open<span>4:45 AM</span></li>
<li><img src="b.svg">Kakad Aarti (Morning)<span>5:15 AM</span></li>
<li><img src="c.svg">Dhoop Aarti<span>At Sunset</span></li>
<li><img src="d.svg">Devotional Songs in Samadhi Mandir<span>8:30 - 10:00 PM</span></li>
<li><img src="e.svg">Shej Aarti<span>10:00 PM</span></li>
</ul>
<p>Help Line No. +91 7588375204</p>
"""

ROOMS = """
<table>
<tr><th>No.</th><th>Location</th><th>Type</th><th>Desc</th><th>Min</th><th>Max</th><th>Rate</th><th>Remark</th></tr>
<tr><td>01.</td><td>Sai Ashram Bhaktiniwas</td><td>AC</td><td>3 beds AC room</td><td>3</td><td>5</td><td>600</td><td>Floor mattress for extra persons</td></tr>
<tr><td>02.</td><td>Sai Bhakta Niwas</td><td>NON AC</td><td>11 beds attached non AC room</td><td>2</td><td>11</td><td></td><td></td></tr>
<tr><td>03.</td><td>Shanti Niketan</td><td>non AC</td><td></td><td>6</td><td>7</td><td>300</td><td></td></tr>
<tr><td>04.</td><td>Shanti Niketan</td><td>non AC</td><td></td><td>6</td><td>7</td><td>300</td><td></td></tr>
<tr><td>05.</td><td>Bus Stand</td><td>NON AC</td><td></td><td>x</td><td>6</td><td>300</td><td></td></tr>
</table>
"""

FAQ = """
<h4>What is general timing of darshan que ?</h4><p>A. Darshan will open from 06:00 AM TO 9:30 PM .</p>
<h4>Prasadalaya?</h4><p>A. Prasadalaya are open from 10:00AM to 10:00 PM</p>
<li>By Airport - Shirdi can be reached from the new Shirdi airport (SAG) just 17 km away.</li>
<li>Kopargaon (at 17 Km distance) and Nagarsul are other stations</li>
<li>new railway station at Sainagar(at 4 Km distance); Manmad-Junction (at 61 Km distance)</li>
"""


def test_programme_rows_and_aarti_tip():
    records, problems = parse_programme(PROGRAMME, URL, "2026-11-12")
    assert [r.place_or_service for r in records] == [
        "Temple Open", "Kakad Aarti (Morning)", "Dhoop Aarti",
        "Devotional Songs in Samadhi Mandir", "Shej Aarti"]
    assert records[2].timing == "At Sunset"
    assert records[3].timing == "8:30 - 10:00 PM"
    assert "four main aartis" in records[1].rule_or_tip
    assert problems == []


def test_rooms_skip_bad_rows_and_duplicates():
    records, problems = parse_rooms(ROOMS, URL, "2026-11-12")
    assert len(records) == 2                      # AC 600 and one Shanti Niketan 300
    assert records[0].cost_inr == 600 and "AC" in records[0].place_or_service
    assert records[1].place_or_service.startswith("Shanti Niketan - non-AC")
    assert len(problems) == 2                     # no rate, and bad capacity 'x'


def test_faq_facts():
    records, problems = parse_faq(FAQ, URL, "2026-11-12")
    by_name = {r.place_or_service: r.timing for r in records}
    assert by_name["Samadhi Mandir darshan queue"] == "06:00 AM to 9:30 PM"
    assert by_name["Shri Saibaba Prasadalaya"] == "10:00AM to 10:00 PM"
    assert by_name["Shirdi airport (SAG)"] == "17 km from Shirdi"
    assert by_name["Sainagar Shirdi railway station"] == "4 km from Shirdi"
    assert problems == []


def test_only_official_domains():
    assert is_official("https://sai.org.in/en/faq")
    assert is_official("https://www.sai.org.in/en/faq")
    assert not is_official("https://sai-org-in.fake.com/en/faq")
    assert not is_official("https://sai.org.in.evil.com/en/faq")

"""Google Trends search interest in app stores, by country, 2004-2024.

Reproduces the "searches" behind the smartphone chart in the FT's "Why birth rates are
falling everywhere all at once" (John Burn-Murdoch, 16 May 2026), whose footnote dates
smartphone take-off from "surveys of smartphone adoption and Google searches for app
stores".

For each country one Trends request compares four search terms (app store, play store,
google play, android market) over 2004-01..2024-12, monthly. Trends scales each request
so its largest monthly value is 100; the four terms share that scale, so their sum is a
consistent within-country index. Values are not comparable across countries.

Responses are cached in FT/data/google_trends/<ISO2>.json; delete a file to refetch it.
Output: FT/intermediate/google_trends_app_stores.csv (country, iso2, month, term, value).
"""

import json
import time

import pandas as pd
import requests

from common.paths import data_dir, intermediate_dir

CACHE = data_dir("FT") / "google_trends"
OUTPUT = intermediate_dir("FT") / "google_trends_app_stores.csv"

TERMS = ["app store", "play store", "google play", "android market"]
TIME = "2004-01-01 2024-12-31"

# ISO2 -> name. The FT's eight countries, then larger countries (population over ~10m)
# with enough Google search volume for Trends to return a series.
COUNTRIES = {
    "US": "US", "GB": "UK", "AU": "Australia", "MX": "Mexico", "ID": "Indonesia",
    "EG": "Egypt", "IR": "Iran", "SN": "Senegal",
    "CA": "Canada", "FR": "France", "DE": "Germany", "IT": "Italy", "ES": "Spain",
    "NL": "Netherlands", "BE": "Belgium", "SE": "Sweden", "PL": "Poland", "CZ": "Czechia",
    "HU": "Hungary", "RO": "Romania", "PT": "Portugal", "GR": "Greece", "TR": "Türkiye",
    "UA": "Ukraine", "RU": "Russia", "JP": "Japan", "KR": "S Korea", "TW": "Taiwan",
    "CN": "China", "TH": "Thailand", "VN": "Viet Nam", "PH": "Philippines", "MY": "Malaysia",
    "IN": "India", "PK": "Pakistan", "BD": "Bangladesh", "LK": "Sri Lanka", "NP": "Nepal",
    "SA": "Saudi Arabia", "IQ": "Iraq", "JO": "Jordan", "MA": "Morocco", "DZ": "Algeria",
    "TN": "Tunisia", "NG": "Nigeria", "GH": "Ghana", "KE": "Kenya", "ET": "Ethiopia",
    "TZ": "Tanzania", "UG": "Uganda", "ZA": "South Africa", "CI": "Cote d'Ivoire",
    "CM": "Cameroon", "BR": "Brazil", "AR": "Argentina", "CL": "Chile", "CO": "Colombia",
    "PE": "Peru", "EC": "Ecuador", "GT": "Guatemala", "VE": "Venezuela", "DO": "Dominican Republic",
    "UZ": "Uzbekistan", "KZ": "Kazakhstan", "AZ": "Azerbaijan",
}


def strip(text):
    """Trends prefixes JSON responses with )]}' to block JSON hijacking."""
    return json.loads(text[text.index("{"):])


def fetch(session, geo):
    req = {
        "comparisonItem": [{"keyword": t, "geo": geo, "time": TIME} for t in TERMS],
        "category": 0,
        "property": "",
    }
    r = session.get(
        "https://trends.google.com/trends/api/explore",
        params={"hl": "en-US", "tz": 0, "req": json.dumps(req)},
    )
    r.raise_for_status()
    widget = next(w for w in strip(r.text)["widgets"] if w["id"] == "TIMESERIES")
    r = session.get(
        "https://trends.google.com/trends/api/widgetdata/multiline",
        params={"hl": "en-US", "tz": 0, "req": json.dumps(widget["request"]), "token": widget["token"]},
    )
    r.raise_for_status()
    return strip(r.text)["default"]["timelineData"]


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0"
    session.get("https://trends.google.com/trends/?geo=US")  # sets the NID cookie

    rows = []
    for geo, name in COUNTRIES.items():
        path = CACHE / f"{geo}.json"
        if not path.exists():
            for attempt in range(4):
                try:
                    path.write_text(json.dumps(fetch(session, geo)), encoding="utf-8")
                    break
                except requests.HTTPError as e:
                    print(f"{geo}: {e}; retrying")
                    time.sleep(30 * (attempt + 1))
            else:
                print(f"{geo}: giving up")
                continue
            time.sleep(3)
        for point in json.loads(path.read_text(encoding="utf-8")):
            month = pd.Timestamp(int(point["time"]), unit="s").strftime("%Y-%m")
            for term, v in zip(TERMS, point["value"]):
                rows.append({"country": name, "iso2": geo, "month": month, "term": term, "value": v})

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUTPUT, index=False)
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()

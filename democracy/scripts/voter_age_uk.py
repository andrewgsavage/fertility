"""Mean/median age of the UK electorate vs. the people who actually vote,
general elections 1964-2024 plus projections to 2074, for
docs/democracy/voter-age.md.

For each election:
  electorate = resident population at or above the voting age (voting-age
               population, not the electoral register)
  voters     = electorate weighted by that election's turnout rate for each
               age band
and the mean and median age of each. Ages are age-last-birthday, so single
year a covers [a, a+1); the median is linearly interpolated within the bin
where the cumulative total crosses 50%.

Population (democracy/data/, gitignored):
  ukpopulationestimates18382025.xlsx -- ONS "UK population estimates, 1838
    to 2025" (pub. 1 Oct 2026). Table 2: UK quinary age, mid-1953 to
    mid-1970 (used for 1964/1966/1970). Table 3: UK single year of age,
    mid-1971 to mid-2025, 90+ open-ended.
  npp2024_uk_ppp_machine_readable.xlsx -- ONS 2024-based national
    population projections, UK principal (pub. 28 Apr 2026), single year of
    age 0-104, 105-109, 110+.
Each election uses the mid-year estimate of its calendar year.

Turnout by age:
  BES -- British Election Study, as tabulated (and scaled to actual turnout)
    in House of Commons Library briefing CBP-8060 "Turnout at elections"
    (10 Jan 2023), section 5.2. 1964-2019.
  Ipsos -- Ipsos/MORI "How Britain Voted" post-election aggregates,
    1992-2024 (self-reported).
"""

import csv
import pathlib

import openpyxl
import plotly.graph_objects as go

DATA_DIR = pathlib.Path("data")
OUTPUT_DIR = pathlib.Path("outputs")
MYE_FILE = DATA_DIR / "ukpopulationestimates18382025.xlsx"
NPP_FILE = DATA_DIR / "npp2024_uk_ppp_machine_readable.xlsx"

# Lower edges of the six turnout age bands used by both BES and Ipsos:
# 18-24, 25-34, 35-44, 45-54, 55-64, 65+. The first band starts at the
# voting age (21-24 in 1964/1966).
BAND_EDGES = [18, 25, 35, 45, 55, 65]

# (label, mid-year used for population, voting age)
ELECTIONS = [
    ("1964", 1964, 21), ("1966", 1966, 21), ("1970", 1970, 18),
    ("Feb 1974", 1974, 18), ("Oct 1974", 1974, 18), ("1979", 1979, 18),
    ("1983", 1983, 18), ("1987", 1987, 18), ("1992", 1992, 18),
    ("1997", 1997, 18), ("2001", 2001, 18), ("2005", 2005, 18),
    ("2010", 2010, 18), ("2015", 2015, 18), ("2017", 2017, 18),
    ("2019", 2019, 18), ("2024", 2024, 18),
]

# % turnout by band, CBP-8060 section 5.2 (BES, scaled to actual turnout).
BES_TURNOUT = {
    "1964": (76.4, 70.7, 79.5, 79.1, 78.4, 76.7),
    "1966": (60.5, 70.8, 80.0, 79.8, 78.0, 75.9),
    "1970": (64.9, 66.5, 72.8, 74.9, 74.1, 77.2),
    "Feb 1974": (70.2, 77.2, 78.7, 73.1, 82.2, 79.2),
    "Oct 1974": (62.5, 69.0, 73.9, 76.6, 76.6, 76.0),
    "1979": (62.5, 72.4, 76.3, 81.2, 81.4, 77.7),
    "1983": (63.9, 67.6, 76.2, 77.6, 77.2, 73.1),
    "1987": (66.6, 74.0, 74.9, 79.9, 78.9, 76.0),
    "1992": (67.3, 77.3, 78.3, 81.8, 78.1, 79.2),
    "1997": (54.1, 62.2, 70.2, 76.4, 79.9, 77.7),
    "2001": (40.4, 45.0, 55.7, 63.2, 64.0, 70.1),
    "2005": (38.2, 47.7, 61.6, 65.5, 72.6, 74.3),
    "2010": (51.8, 57.3, 64.4, 67.5, 69.8, 74.7),
    "2015": (51.6, 51.8, 60.6, 70.1, 74.4, 79.3),
    "2017": (48.6, 50.6, 59.6, 70.7, 82.5, 85.2),
    "2019": (54.5, 54.4, 60.9, 71.0, 72.8, 78.5),
}

# % turnout by band, Ipsos/MORI "How Britain Voted <year>".
IPSOS_TURNOUT = {
    "1992": (63, 76, 80, 80, 82, 83),
    "1997": (51, 64, 73, 79, 80, 79),
    "2001": (39, 46, 59, 65, 69, 70),
    "2005": (37, 49, 61, 65, 71, 75),
    "2010": (44, 55, 66, 69, 73, 76),
    "2015": (43, 54, 64, 72, 77, 78),
    "2017": (54, 55, 56, 66, 71, 71),
    "2019": (47, 55, 54, 63, 66, 74),
    "2024": (37, 41, 48, 55, 64, 73),
}

PROJECTION_YEARS = list(range(2029, 2075, 5))
PROJECTION_TURNOUT = IPSOS_TURNOUT["2024"]
# Placeholder for 16-17s under votes-at-16: 2024's 18-24 rate.
TURNOUT_16_17 = PROJECTION_TURNOUT[0]

# Upper edges given to open-ended top age groups, so they act as a uniform
# bin (mean = midpoint). Only affects means, never the medians.
OPEN_TOP_85 = 92   # 1960s quinary "85 and over" -> mean 88.5
OPEN_TOP_90 = 95   # MYE "90 and over" -> mean 92.5
OPEN_TOP_105 = 110  # NPP 105-109 and 110+ folded together -> mean 107.5


# --- Population -------------------------------------------------------------
# A population is a list of (age_lo, age_hi, count) bins.

def _mye_columns(ws):
    rows = list(ws.iter_rows(values_only=True))
    header = rows[1]
    persons = [r for r in rows[2:] if r[1] == "Persons" and r[0] != "All Ages"]
    return header, persons


def load_mye():
    wb = openpyxl.load_workbook(MYE_FILE, read_only=True)
    pops = {}

    header, persons = _mye_columns(wb["Table 3"])
    for col, name in enumerate(header):
        if not (isinstance(name, str) and name.startswith("Mid-")):
            continue
        bins = []
        for r in persons:
            age, count = r[0], r[col]
            if age == "90 and over":
                bins.append((90, OPEN_TOP_90, count))
            else:
                bins.append((int(age), int(age) + 1, count))
        pops[int(name[4:])] = bins

    header, persons = _mye_columns(wb["Table 2"])
    for col, name in enumerate(header):
        if not (isinstance(name, str) and name.startswith("Mid-")):
            continue
        # Older columns of Table 2 are in thousands, newer ones in units.
        scale = 1000 if persons[0][col] < 100_000 else 1
        bins = []
        for r in persons:
            age, count = r[0], r[col]
            if age == "85 and over":
                bins.append((85, OPEN_TOP_85, count * scale))
            else:
                lo, hi = (int(x) for x in age.split(" to "))
                bins.append((lo, hi + 1, count * scale))
        pops.setdefault(int(name[4:]), bins)
    return pops


def load_npp():
    wb = openpyxl.load_workbook(NPP_FILE, read_only=True)
    rows = list(wb["Population"].iter_rows(values_only=True))
    header = rows[0]
    pops = {}
    for col, name in enumerate(header):
        if not (isinstance(name, str) and name.isdigit()):
            continue
        by_age = {}
        for r in rows[1:]:
            if r[0] not in ("Males", "Females"):
                continue
            age = r[1]
            key = int(age) if age.isdigit() else 105  # "105 - 109", "110+"
            by_age[key] = by_age.get(key, 0) + r[col]
        pops[int(name)] = [
            (a, OPEN_TOP_105 if a == 105 else a + 1, n)
            for a, n in sorted(by_age.items())
        ]
    return pops


# --- Weighting --------------------------------------------------------------

def _split_at(bins, edges):
    """Split bins at the given ages, assuming a uniform spread within each
    bin, so no bin straddles a franchise or turnout-band edge."""
    out = []
    for lo, hi, n in bins:
        cuts = [lo] + [e for e in edges if lo < e < hi] + [hi]
        for a, b in zip(cuts, cuts[1:]):
            out.append((a, b, n * (b - a) / (hi - lo)))
    return out


def weighted_bins(pop, voting_age, turnout=None, turnout_16_17=None):
    """(lo, hi, weight) bins of the electorate, weighted by turnout rate if
    `turnout` (six band percentages) is given."""
    edges = sorted(set([voting_age] + BAND_EDGES))
    out = []
    for lo, hi, n in _split_at(pop, edges):
        if lo < voting_age:
            continue
        if turnout is None:
            w = 1.0
        elif lo < BAND_EDGES[0]:
            w = turnout_16_17 / 100
        else:
            band = max(i for i, e in enumerate(BAND_EDGES) if lo >= e)
            w = turnout[band] / 100
        out.append((lo, hi, n * w))
    return out


def mean_age(bins):
    total = sum(w for _, _, w in bins)
    return sum((lo + hi) / 2 * w for lo, hi, w in bins) / total


def median_age(bins):
    half = sum(w for _, _, w in bins) / 2
    cum = 0.0
    for lo, hi, w in bins:
        if cum + w >= half:
            return lo + (hi - lo) * (half - cum) / w
        cum += w
    raise ValueError("empty population")


def summarise(pop, voting_age, turnout, turnout_16_17=None):
    electorate = weighted_bins(pop, voting_age)
    voters = weighted_bins(pop, voting_age, turnout, turnout_16_17)
    n_elec = sum(w for _, _, w in electorate)
    n_vote = sum(w for _, _, w in voters)
    return {
        "mean_electorate_age": mean_age(electorate),
        "median_electorate_age": median_age(electorate),
        "mean_voter_age": mean_age(voters),
        "median_voter_age": median_age(voters),
        "electorate": n_elec,
        "est_voters": n_vote,
        "implied_turnout_pct": 100 * n_vote / n_elec,
    }


def build_rows():
    mye = load_mye()
    npp = load_npp()
    rows = []
    for label, year, voting_age in ELECTIONS:
        pop = mye[year]
        pop_basis = (
            f"ONS mid-{year} estimate, 5-year bands split uniformly"
            if year <= 1970 else f"ONS mid-{year} estimate, single year of age"
        )
        for source, table, desc in (
            ("BES", BES_TURNOUT, "BES turnout via HoC Library CBP-8060"),
            ("Ipsos", IPSOS_TURNOUT, f"Ipsos How Britain Voted {label}"),
        ):
            if label not in table:
                continue
            rows.append({
                "election": label, "year": year, "status": "actual",
                "voting_age": voting_age, "turnout_source": source,
                **summarise(pop, voting_age, table[label]),
                "basis": f"{pop_basis}; {desc}",
            })
    for year in PROJECTION_YEARS:
        pop = npp[year]
        for voting_age in (18, 16):
            basis = (
                f"ONS 2024-based principal projection, mid-{year}; "
                "ASSUMPTION: Ipsos 2024 turnout by age held flat"
            )
            if voting_age == 16:
                basis += f"; 16-17s at {TURNOUT_16_17:g}% (2024's 18-24 rate)"
            rows.append({
                "election": str(year), "year": year, "status": "projected",
                "voting_age": voting_age, "turnout_source": "Ipsos 2024 held flat",
                **summarise(pop, voting_age, PROJECTION_TURNOUT, TURNOUT_16_17),
                "basis": basis,
            })
    return rows


# --- Outputs ----------------------------------------------------------------

# Polling-day x positions, so the two 1974 elections don't share a point.
X_POS = {"Feb 1974": 1974.16, "Oct 1974": 1974.78}

ELECTORATE_COLOR = "#2a78d6"
BES_COLOR = "#eb6834"
IPSOS_COLOR = "#1baf7a"


def _x(row):
    return X_POS.get(row["election"], row["year"] + 0.5)


def _trace(rows, key, name, color, dash="solid", legendgroup=None):
    return go.Scatter(
        x=[_x(r) for r in rows], y=[r[key] for r in rows],
        customdata=[r["election"] for r in rows],
        mode="lines+markers", name=name, legendgroup=legendgroup,
        line=dict(width=2, color=color, dash=dash), marker=dict(size=8),
        hovertemplate=f"{name}<br>%{{customdata}}: %{{y:.1f}}<extra></extra>",
    )


def _figure(rows, stat):
    key_e, key_v = f"{stat}_electorate_age", f"{stat}_voter_age"
    actual = [r for r in rows if r["status"] == "actual"]
    electorate = [r for r in actual if r["turnout_source"] == "BES"] + [
        r for r in actual if r["election"] == "2024"
    ]
    bes = [r for r in actual if r["turnout_source"] == "BES"]
    ipsos = [r for r in actual if r["turnout_source"] == "Ipsos"]
    ipsos_2024 = [r for r in ipsos if r["election"] == "2024"]
    proj18 = [r for r in rows if r["status"] == "projected" and r["voting_age"] == 18]
    proj16 = [r for r in rows if r["status"] == "projected" and r["voting_age"] == 16]
    elec_2024 = [r for r in actual if r["election"] == "2024"][:1]

    fig = go.Figure([
        _trace(electorate, key_e, "Electorate", ELECTORATE_COLOR),
        _trace(bes, key_v, "Voters (BES turnout)", BES_COLOR),
        _trace(ipsos, key_v, "Voters (Ipsos turnout)", IPSOS_COLOR),
        _trace(elec_2024 + proj18, key_e, "Electorate, projected", ELECTORATE_COLOR, "dash"),
        _trace(ipsos_2024 + proj18, key_v, "Voters, projected", IPSOS_COLOR, "dash"),
        _trace(elec_2024 + proj16, key_e, "Electorate, votes at 16", ELECTORATE_COLOR, "dot"),
        _trace(ipsos_2024 + proj16, key_v, "Voters, votes at 16", IPSOS_COLOR, "dot"),
    ])
    fig.add_vrect(
        x0=2025, x1=2075, fillcolor="#888888", opacity=0.08, line_width=0,
        annotation_text="Projection: 2024 turnout by age held flat",
        annotation_position="top left", annotation_font_size=11,
    )
    fig.add_vline(
        x=1969.5, line=dict(width=1, color="#999999", dash="dash"),
        annotation_text="Voting age 21 → 18", annotation_position="bottom right",
        annotation_font_size=11,
    )
    fig.update_xaxes(title_text="General election", range=[1962, 2076], dtick=10)
    fig.update_yaxes(title_text=f"{stat.capitalize()} age (years)")
    fig.update_layout(
        title=f"{stat.capitalize()} age of UK electorate vs voters",
        template="plotly_white", autosize=True, hovermode="closest",
        legend=dict(orientation="h", yanchor="top", y=-0.15, x=0),
        margin=dict(b=120),
    )
    return fig


def _save_html(fig, name):
    output = OUTPUT_DIR / name
    fig.write_html(
        output, include_plotlyjs="cdn", full_html=True,
        default_width="100%", default_height="100%",
        config={"responsive": True},
    )
    html = output.read_text(encoding="utf-8")
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    output.write_text(html, encoding="utf-8")
    print(f"Saved {output}")


def _table_markdown(rows):
    header = (
        "| Election | Voting age | Turnout source | Mean electorate | Median electorate "
        "| Mean voter | Median voter | Basis |"
    )
    lines = [header, "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(
            f"| {r['election']} | {r['voting_age']} | {r['turnout_source']} "
            f"| {r['mean_electorate_age']:.1f} | {r['median_electorate_age']:.1f} "
            f"| {r['mean_voter_age']:.1f} | {r['median_voter_age']:.1f} | {r['basis']} |"
        )
    return "\n".join(lines) + "\n"


def _turnout_markdown():
    lines = [
        "| Election | Source | 18-24 | 25-34 | 35-44 | 45-54 | 55-64 | 65+ |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for label, _, _ in ELECTIONS:
        for source, table in (("BES", BES_TURNOUT), ("Ipsos", IPSOS_TURNOUT)):
            if label in table:
                cells = " | ".join(f"{v:g}" for v in table[label])
                lines.append(f"| {label} | {source} | {cells} |")
    return "\n".join(lines) + "\n"


def _save_csv(rows):
    output = OUTPUT_DIR / "voter_age_uk.csv"
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        for r in rows:
            writer.writerow({
                k: round(v, 2) if isinstance(v, float) else v for k, v in r.items()
            })
    print(f"Saved {output}")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(exist_ok=True)
    rows = build_rows()
    _save_csv(rows)
    _save_html(_figure(rows, "median"), "voter_age_uk_median.html")
    _save_html(_figure(rows, "mean"), "voter_age_uk_mean.html")
    # .txt, not .md -- see half_life_tfr.py.
    for name, text in (
        ("voter_age_uk_table.txt", _table_markdown(rows)),
        ("voter_age_uk_turnout_table.txt", _turnout_markdown()),
    ):
        (OUTPUT_DIR / name).write_text(text, encoding="utf-8")
        print(f"Saved {OUTPUT_DIR / name}")

import functools

import pandas as pd

COUNTRY_NAMES = {
    "AUT": "Austria",
    "BEL": "Belgium",
    "BGR": "Bulgaria",
    "BLR": "Belarus",
    "CAN": "Canada",
    "CHE": "Switzerland",
    "CHL": "Chile",
    "CZE": "Czechia",
    "DEUTE": "Germany, East",
    "DEUTW": "Germany, West",
    "DEUTNP": "Germany",
    "DNK": "Denmark",
    "ESP": "Spain",
    "EST": "Estonia",
    "FIN": "Finland",
    "GBRTENW": "England and Wales",
    "GBR_NIR": "Northern Ireland",
    "GBR_NP": "United Kingdom",
    "GBR_SCO": "Scotland",
    "HRV": "Croatia",
    "HUN": "Hungary",
    "IRL": "Ireland",
    "ISL": "Iceland",
    "ITA": "Italy",
    "JPN": "Japan",
    "KOR": "South Korea",
    "LTU": "Lithuania",
    "NLD": "Netherlands",
    "NOR": "Norway",
    "POL": "Poland",
    "PRT": "Portugal",
    "RUS": "Russia",
    "SVK": "Slovakia",
    "SVN": "Slovenia",
    "SWE": "Sweden",
    "TWN": "Taiwan",
    "UKR": "Ukraine",
    "USA": "United States",
    # Not an HFD code — a conditional-ASFR reconstruction from ONS cohort
    # data injected into the mi.txt-derived dataframe by
    # cond_asfr_region_grid.py (see its load_data()), since HFD itself has
    # no conditional-ASFR tables for the UK.
    "UK_ONS": "England & Wales",
}


# Geographic groupings (roughly 5 countries per group) for the codes present
# in the conditional ASFR source data (data/HFD/mi.txt). Codes in
# COUNTRY_NAMES that aren't in that file (e.g. ITA, the GBR_* variants,
# DEUTW/DEUTNP) are omitted here, as are DEUTE (Germany, East), RUS, BLR, UKR,
# SVK, POL, and ISL. UK_ONS is the one exception — it's not in mi.txt either,
# but cond_asfr_region_grid.py injects it separately (see load_data()).
#
# Former-communist countries (Eastern Bloc / Yugoslavia) are kept in their
# own groups, separate from non-communist countries, even where that breaks
# from pure geography (e.g. Iberia is split out from the Balkans). The
# Baltic states are the exception — grouped with the Nordics rather than
# Eastern Europe, matching how they're commonly discussed together
# (Nordic-Baltic cooperation) despite their Soviet-era history.
COUNTRY_REGIONS = {
    # Non-Europe
    "Americas & East Asia": ["CAN", "USA", "CHL", "JPN", "KOR", "TWN"],
    # Non-communist, plus the Baltics
    "Nordic & Baltic": ["DNK", "FIN", "NOR", "SWE", "EST", "LTU"],
    "Western Europe": ["BEL", "IRL", "NLD", "AUT", "CHE", "ESP", "PRT", "UK_ONS"],
    # Former communist
    "Eastern Europe": ["CZE", "HUN", "SVN", "BGR", "HRV"],
}

_CODE_TO_REGION = {code: region for region, codes in COUNTRY_REGIONS.items() for code in codes}


def region_for(code):
    """The geographic region name for an HFD-style country code, or None if
    the code isn't in COUNTRY_REGIONS."""
    return _CODE_TO_REGION.get(code)


def order_by_region(codes):
    """Sort country codes by geographic region (in COUNTRY_REGIONS order),
    then alphabetically within a region. Codes with no assigned region are
    appended alphabetically at the end."""
    region_order = {region: i for i, region in enumerate(COUNTRY_REGIONS)}

    def key(code):
        region = _CODE_TO_REGION.get(code)
        if region is None:
            return (1, "", code)
        return (0, region_order[region], code)

    return sorted(codes, key=key)


def country_title(code, year_min=None, year_max=None, suffix=None, cpfr1=None, asfr1_20=None):
    """Build a chart title from an HFD-style country code: full name, the
    year range of the data actually being displayed, and (optionally) a
    2015 stats line with the CPFR1 value used to rank the country and its
    ASFR1 at age 20."""
    name = COUNTRY_NAMES.get(code, code)
    if year_min is not None and year_max is not None and not pd.isna(year_min) and not pd.isna(year_max):
        title = f"{name} ({int(year_min)}–{int(year_max)})"
    else:
        title = name
    stats = []
    if cpfr1 is not None and not pd.isna(cpfr1):
        stats.append(f"CPFR:{cpfr1:.2f}")
    if asfr1_20 is not None and not pd.isna(asfr1_20):
        stats.append(f"ASFR1@20:{asfr1_20:.3f}")
    if stats:
        title = f"{title}\n{', '.join(stats)}"
    if suffix:
        title = f"{title}\n{suffix}"
    return title


@functools.lru_cache(maxsize=None)
def _cpfr1_max_by_country(year):
    cpfr = pd.read_csv(
        "data/HFD/cpfrVVbo.txt",
        sep=r"\s+",
        skiprows=3,
        names=["code", "year", "age", "cohort", "cpfr", "cpfr1", "cpfr2", "cpfr3", "cpfr4", "cpfr5p"],
        na_values=".",
    )
    return cpfr[cpfr["year"] == year].groupby("code")["cpfr1"].max()


def order_by_cpfr1(codes, year=2015):
    """Sort country codes by their highest cumulative first-birth rate
    (CPFR1) observed in `year`, richest first. Codes with no data for that
    year are appended alphabetically at the end."""
    ranking = _cpfr1_max_by_country(year)

    def key(code):
        value = ranking.get(code)
        if value is None or pd.isna(value):
            return (1, code, 0.0)
        return (0, "", -value)

    return sorted(codes, key=key)


def cpfr1_value(code, year=2015):
    """The CPFR1 value used to order/annotate `code`, or None if unavailable."""
    value = _cpfr1_max_by_country(year).get(code)
    if value is None or pd.isna(value):
        return None
    return value


@functools.lru_cache(maxsize=None)
def _asfr1_at_age_by_country(age, year):
    mi = pd.read_csv(
        "data/HFD/mi.txt",
        sep=r"\s+",
        skiprows=3,
        names=["code", "year", "age", "m1x", "m2x", "m3x", "m4x", "m5px"],
        na_values=".",
    )
    mi["age"] = mi["age"].astype(str).str.replace("-", "", regex=False).str.replace("+", "", regex=False).astype(int)
    subset = mi[(mi["year"] == year) & (mi["age"] == age)]
    return subset.set_index("code")["m1x"]


def asfr1_value(code, age=20, year=2015):
    """The conditional ASFR1 (first-birth rate) for `code` at `age` in `year`,
    or None if unavailable."""
    value = _asfr1_at_age_by_country(age, year).get(code)
    if value is None or pd.isna(value):
        return None
    return value


def order_by_asfr1_20(codes, age=20, year=2015):
    """Sort country codes by their ASFR1 (first-birth rate) at `age` in
    `year`, richest first. Codes with no data for that year/age are
    appended alphabetically at the end."""
    ranking = _asfr1_at_age_by_country(age, year)

    def key(code):
        value = ranking.get(code)
        if value is None or pd.isna(value):
            return (1, code, 0.0)
        return (0, "", -value)

    return sorted(codes, key=key)

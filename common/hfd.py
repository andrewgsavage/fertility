"""Human Fertility Database (humanfertility.org) .txt tables, from the all-countries zip
unpacked into HFD/data/HFD/ (not tracked in git)."""

import pandas as pd

from common.paths import REPO

HFD_DIR = REPO / "HFD" / "data" / "HFD"


def read_hfd(name, names=None, *, directory=HFD_DIR, na_values=".", **kwargs):
    """Read an HFD whitespace-separated table: two title lines, a header row, then data
    ("." = missing).

    names: column names to use in place of the file's header row (which is then skipped).
    Other keyword arguments go to pd.read_csv.
    """
    if names is None:
        return pd.read_csv(directory / name, sep=r"\s+", skiprows=2, na_values=na_values, **kwargs)
    return pd.read_csv(directory / name, sep=r"\s+", skiprows=3, names=names, na_values=na_values, **kwargs)


def age_to_int(ages):
    """HFD open-ended ages ("12-", "55+") as ints."""
    return ages.astype(str).str.strip("-+").astype(int)


def load_asfr(codes=("GBRTENW",)):
    """Period ASFR (asfrRR.txt) for the given countries (default England & Wales), one row per
    code x year x age, with cohort = year - age."""
    df = read_hfd("asfrRR.txt", ["code", "year", "age", "asfr"])
    df["age"] = age_to_int(df["age"])
    df["cohort"] = df["year"] - df["age"]
    df = df[df["code"].isin(codes)]
    return df

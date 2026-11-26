"""Uruguay: births by mother's education and birth order, 2013 and 2021, from the Perinatal
Information System (SIP) public microdata.

SIP records "Estudios" (VAR_0013: none, primary, secondary, university; numeric codes in 2013,
labels in 2021) and previous deliveries (VAR_0046). Births with no education recorded are
dropped; "none" is folded into primary. These are counts, not rates: the number of women in
each education group changed too, so a fall in births in a group mixes lower fertility with a
smaller group.

Input: SIP 2013 and 2021 (fetched and cached by uruguay_by_order.py).
Output: HFC/outputs/ury_births_by_education.csv.
"""

import sys

import pandas as pd

from common.paths import REPO, outputs_dir

sys.path.insert(0, str(REPO / "HFC" / "scripts"))
from uruguay_by_order import SIP_URLS, unrar  # noqa: E402

EDU = {1: "Primary or less", 2: "Primary or less", 3: "Secondary", 4: "University",
       "Ninguno": "Primary or less", "Primaria": "Primary or less", "Secundaria": "Secondary",
       "Universidad": "University"}
ORDER = {1: "First", 2: "Second", 3: "Third+"}


def sip(year):
    csv = unrar(SIP_URLS[year], f"sip_{year}", "*.csv")
    d = pd.read_csv(csv, sep=";", encoding="latin-1", low_memory=False, usecols=["VAR_0013", "VAR_0046"])
    code = pd.to_numeric(d.VAR_0013, errors="coerce").fillna(d.VAR_0013)
    prev = pd.to_numeric(d.VAR_0046, errors="coerce")
    d = d.assign(edu=code.map(EDU), order=(prev + 1).clip(upper=3).where(prev.lt(99)).map(ORDER))
    return d.dropna(subset=["edu"])


def main():
    rows = []
    for year in SIP_URLS:
        d = sip(year)
        for edu, g in d.groupby("edu"):
            rows.append({"year": year, "edu": edu, "order": "All", "births": len(g)})
            for order, n in g.order.value_counts().items():
                rows.append({"year": year, "edu": edu, "order": order, "births": n})
    t = pd.DataFrame(rows).pivot_table(index=["order", "edu"], columns="year", values="births", aggfunc="sum")
    t["change_pct"] = (100 * (t[2021] / t[2013] - 1)).round(1)
    for y in SIP_URLS:  # share of that order's births with a recorded education
        t[f"share_{y}"] = (100 * t[y] / t[y].groupby(level="order").transform("sum")).round(1)
    out = outputs_dir("HFC")
    out.mkdir(parents=True, exist_ok=True)
    t.to_csv(out / "ury_births_by_education.csv")
    print(t.to_string())


if __name__ == "__main__":
    main()

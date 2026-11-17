"""England & Wales abortions by age group and parity, 2013-2023, from DHSC Table 2.

DHSC publishes age by parity (number of previous pregnancies ending in a live
birth or stillbirth) only in each year's own data tables, and only for three age
groups: Under 20, 20-34 and 35 and over. This script reads Table 2 from each
year's file and writes one series.

Inputs (ONS/data/dhsc/, not tracked in git), from
https://www.gov.uk/government/collections/abortion-statistics-in-england-and-wales :
  2013.xls   .../media/5a7cfe33ed915d321c2de2b2/2013_complete_tables.xls
  2014.xlsx  .../media/5a801a13ed915d74e622c7a1/2014_complete_tables.xlsx
  2015.xlsx  .../media/5a805674e5274a2e87db93df/Updated_2015_complete_tables.xlsx
  2016.xlsx  .../media/5a79a25be5274a3864fd87c9/Abortion_statistics_2016_data_tables.ods.xlsx
  2017.ods   .../media/682dc942baff3dab9977515b/2017-abortion-statistics-data-tables-revised-may-2025.ods
  2018.ods   .../media/5d011452ed915d097897ccfe/2018_Abortion_Statistics_-_Data_tables__1_.ods
  2019.ods   .../media/5f5267958fa8f535e75a3fb9/abortion-statistics-2019-data-tables.ods
  2020.ods   .../media/60c0878b8fa8f57ce63f18a4/abortion-statistics-2020-data-tables_Final.ods
  2021.ods   .../media/6880f4a6901d5f8d47120555/abortion-statistics-2021-data-tables-revision-July-2025.ods
  2022.ods   .../media/67ed5704199d1cd55b48c6ad/abortion-statistics-2022-data-tables-amended-03-april-2025.ods
  2023.ods   abortion-statistics-2023-england-and-wales-residents.ods (see abortion_share_uk.py)
  (media URLs are under https://assets.publishing.service.gov.uk)

Output: ONS/outputs/dhsc_parity_by_age.csv  year, age, parity (0 / 1+), abortions
Run with xlrd available for the 2013 .xls file, e.g.
  pixi exec --spec python=3.12 --spec xlrd --spec openpyxl --spec pandas python ONS/scripts/dhsc_parity_by_age.py
(without xlrd, 2013 is skipped).
"""

import pathlib
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

import pandas as pd

_ROOT = pathlib.Path(__file__).resolve().parent.parent
D = _ROOT / "data" / "dhsc"
OUT = _ROOT / "outputs" / "dhsc_parity_by_age.csv"
T = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
P = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p"
SHEETS = {"Table_2", "T2", "Table 2"}
AGES = ["All ages", "Under 20", "20–34", "35+"]


def rows_ods(path):
    root = ET.fromstring(zipfile.ZipFile(path).read("content.xml"))
    t = next(t for t in root.iter(T + "table") if t.get(T + "name") in SHEETS)
    out = []
    for r in t.iter(T + "table-row"):
        row = []
        for c in r:
            rep = int(c.get(T + "number-columns-repeated", "1"))
            row += [" ".join("".join(p.itertext()) for p in c.iter(P))] * min(rep, 30)
        out.append(row)
    return out


def rows_xlsx(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[next(n for n in wb.sheetnames if n in SHEETS)]
    return [["" if v is None else str(v) for v in r] for r in ws.iter_rows(values_only=True)]


def rows_xls(path):
    import xlrd
    wb = xlrd.open_workbook(path)
    s = wb.sheet_by_name(next(n for n in wb.sheet_names() if n in SHEETS))
    return [[str(v) for v in s.row_values(i)] for i in range(s.nrows)]


def num(c):
    c = c.replace(",", "").strip()
    try:
        return float(c)
    except ValueError:
        return None


def parse(rows):
    """{parity label: [all, under 20, 20-34, 35+]} from the (vii) Parity block."""
    out = {}
    inside = False
    for r in rows:
        cells = [c.strip() for c in r if c is not None]
        first = next((c for c in cells if c), "")
        if re.match(r"(\(vii\)\s*)?Parity\s*\(", first, re.I):
            if len(cells) > 3 and any(num(c) is not None for c in cells[2:]):
                # 2021+ layout: section, breakdown, then number/% pairs on one row
                vals = [num(c) for c in cells[1:] if c]
                label, nums = cells[cells.index(first) + 1], [v for v in vals[1:]]
                out[label] = nums[0::2][:4]
            else:
                inside = True  # 2013-2020 layout: header row, then one row per parity
            continue
        if inside:
            if re.match(r"(\(viii\)|Number of previous)", first, re.I):
                break
            vals = [num(c) for c in cells if c]
            if first and vals and vals[0] is None and sum(v is not None for v in vals) >= 8:
                nums = [v for v in vals[1:] if v is not None]
                out[first] = nums[0::2][:4]
            elif first and num(first) is not None and sum(v is not None for v in vals) >= 9:
                # label is a number ("0", "1"): first value is the label
                nums = [v for v in vals[1:] if v is not None]
                out[first.split(".")[0]] = nums[0::2][:4]
    return out


def load():
    recs = []
    for f in sorted(D.iterdir()):
        y = int(f.stem[:4])
        reader = {".ods": rows_ods, ".xlsx": rows_xlsx, ".xls": rows_xls}[f.suffix]
        try:
            blk = parse(reader(f))
        except ImportError:
            print(f"{f.name}: needs xlrd, skipped")
            continue
        zero = blk.get("0")
        assert zero and len(zero) == 4, (f.name, blk)
        known = [sum(v[i] for v in blk.values()) for i in range(4)]
        for i, a in enumerate(AGES):
            recs.append((y, a, "0", zero[i]))
            recs.append((y, a, "1+", known[i] - zero[i]))
        print(y, {k: v for k, v in blk.items()})
    return pd.DataFrame(recs, columns=["year", "age", "parity", "abortions"])


if __name__ == "__main__":
    d = load()
    OUT.parent.mkdir(exist_ok=True)
    d.to_csv(OUT, index=False)
    p = d.pivot_table(index=["age", "parity"], columns="year", values="abortions")
    print(p.to_string())
    print(OUT)

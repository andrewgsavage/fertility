"""England & Wales abortions (DHSC abortion statistics) and births (HFD), shared by
ONS/scripts/abortion_share_uk.py and the eurostat abortion charts.

Inputs (not in git):
  ONS/data/abortion-statistics-2023-england-and-wales-residents.ods
      https://www.gov.uk/government/statistics/abortion-statistics-for-england-and-wales-2023
  HFD/data/HFD/birthsRR.txt  (Human Fertility Database, all-countries zip)
"""

import re
import zipfile
import xml.etree.ElementTree as ET

from common.hfd import HFD_DIR
from common.paths import data_dir

ODS = data_dir("ONS") / "abortion-statistics-2023-england-and-wales-residents.ods"
HFD_BIRTHS = HFD_DIR / "birthsRR.txt"

# ONS Births in England and Wales: 2023 (HFD ends at 2022).
ONS_BIRTHS = {2023: 591_072}

_T = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
_O = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}"
_P = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p"


def read_ods_sheet(path, sheet):
    """Rows of a sheet in an .ods file as lists of strings (stdlib only)."""
    root = ET.fromstring(zipfile.ZipFile(path).read("content.xml"))
    for table in root.iter(_T + "table"):
        if table.get(_T + "name") != sheet:
            continue
        rows = []
        for r in table.iter(_T + "table-row"):
            row = []
            for c in r.iter(_T + "table-cell"):
                n = min(int(c.get(_T + "number-columns-repeated", "1")), 50)
                v = c.get(_O + "value") or "".join(p.text or "" for p in c.iter(_P))
                row += [v] * n
            rows.append(row)
        return rows
    raise KeyError(sheet)


def year_of(s):
    m = re.match(r"(\d{4})", s)
    return int(m.group(1)) if m else None


def abortions_total():
    """{year: abortions to E&W residents}, Table 1."""
    out = {}
    for row in read_ods_sheet(ODS, "Table_1"):
        if len(row) > 2 and year_of(row[0]) and row[2].isdigit():
            out[year_of(row[0])] = int(row[2])
    return out


def births():
    """{year: {age: births}} for England & Wales from HFD."""
    out = {}
    with open(HFD_BIRTHS, encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) == 4 and parts[0] == "GBRTENW":
                age = int(re.sub(r"\D", "", parts[2]))
                out.setdefault(int(parts[1]), {})[age] = float(parts[3])
    return out

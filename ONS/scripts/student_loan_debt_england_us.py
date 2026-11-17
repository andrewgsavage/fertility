"""Student loan debt: England (average balance per borrower) and the US (total outstanding).

England: Student Loans Company, "Student Loans in England: Financial Year 2024-25", Table 5A
  (income-contingent-repayment borrowers with a loan balance, as at end of financial year; 2024-25 is suppressed).
  https://assets.publishing.service.gov.uk/media/6a44cbd66c5c6d8122b81573/slcsp012025.xlsx
US: Federal Reserve Board, Student Loans Owned and Securitized, Outstanding (SLOAS), via FRED; Q4 value each year.
  https://fred.stlouisfed.org/graph/fredgraph.csv?id=SLOAS

Inputs (download into ONS/data/ - not tracked in git):
  slc_england_2025.xlsx, fred_SLOAS.csv
"""

import pathlib
import shutil

import openpyxl
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
DATA = _SCRIPT_DIR.parent / "data"
OUTPUT = _SCRIPT_DIR.parent / "outputs" / "student_loan_debt_england_us.html"
DOCS = _SCRIPT_DIR.parent.parent / "docs" / "_static" / "ons" / "student_loan_debt_england_us.html"


def england():
    ws = openpyxl.load_workbook(DATA / "slc_england_2025.xlsx", read_only=True)["Table 5A (i)(ii)(iii)"]
    rows = list(ws.iter_rows(values_only=True))
    years = [y for y in rows[7][3:] if y]
    totals = [i for i, r in enumerate(rows) if r[1] and str(r[1]).startswith("All ICR borrowers with a loan balance")]
    names = ["borrowers_k", "owed_m", "avg"]
    d = pd.DataFrame({"fy": years})
    for n, i in zip(names, totals):
        d[n] = pd.to_numeric(pd.Series(rows[i][3:3 + len(years)]), errors="coerce")
    d["year"] = d.fy.str[:4].astype(int) + 1  # year in which the financial year ends
    return d.dropna(subset=["avg"])


def us():
    d = pd.read_csv(DATA / "fred_SLOAS.csv", parse_dates=["observation_date"])
    d = d[d.observation_date.dt.month == 10]  # Q4 observation is dated 1 October
    d["year"] = d.observation_date.dt.year
    d["bn"] = d.SLOAS / 1000
    return d


def plot(e, u):
    fig = make_subplots(rows=1, cols=2, subplot_titles=(
        "England: average loan balance per borrower (GBP, nominal)",
        "US: total student loans outstanding (USD bn, nominal)"), horizontal_spacing=0.12)
    fig.add_trace(go.Scatter(x=e.year, y=e.avg, mode="lines+markers", name="England",
                             line=dict(color="#1f77b4", width=2.5),
                             customdata=e.borrowers_k,
                             hovertemplate="England, FY ending %{x}: GBP %{y:,.0f} per borrower"
                                           " (%{customdata:,.0f}k borrowers)<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(x=u.year, y=u.bn, mode="lines+markers", name="US",
                             line=dict(color="#d62728", width=2.5),
                             hovertemplate="US Q4 %{x}: USD %{y:,.0f}bn<extra></extra>"), row=1, col=2)
    fig.update_yaxes(rangemode="tozero", row=1, col=1)
    fig.update_yaxes(rangemode="tozero", row=1, col=2)
    fig.update_layout(template="plotly_white", showlegend=False, margin=dict(t=60), hovermode="closest")
    return fig


if __name__ == "__main__":
    e, u = england(), us()
    fig = plot(e, u)
    fig.write_html(OUTPUT, include_plotlyjs="cdn", full_html=True, default_width="100%",
                   default_height="100%", config={"responsive": True})
    html = OUTPUT.read_text(encoding="utf-8")
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    OUTPUT.write_text(html, encoding="utf-8")
    DOCS.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(OUTPUT, DOCS)
    print(f"Saved {OUTPUT}")
    print(e.to_string())
    print(u[["year", "bn"]].to_string())

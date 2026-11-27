"""Young-age fertility around major family-policy changes, by policy domain.

For each change in research/data/policy_events.csv (domains cash, leave, childcare, housing;
direction pro or cut), the rate in the country at each year from 4 before to 4 after the year
the change took effect, as % difference from the year before it (t = -1), minus the same change
averaged over all other countries in the same calendar years. Averaged over changes, pro and cut
separately.

Rates: ASFR 20-24 and 25-29, all births and first births, from country_timelines (Eurostat,
HFD, HFC, Uruguay). A change is used for a rate only if that rate exists for t = -1 and t = 0.

Outputs (eurostat/outputs/): policy_event_study_<domain>.html; policy_event_study.csv (one row
per change, rate and t); policy_event_study_summary.csv (change in trend, slope over t = -1..4 minus
slope over t = -4..-1, by domain, direction and rate).
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.plotting import write_html
from country_timelines import ROWS, load_events, load_first
from smartphone_milestones import COUNTRIES, FALL, HFD_CODES, RISE, load_asfr
from young_fertility import OUTDIR

DOMAINS = {"cash": "Cash benefits", "leave": "Parental leave", "childcare": "Childcare", "housing": "Housing"}
WINDOW = range(-4, 5)
COLOR = {"pro": RISE, "cut": FALL}
NAME = {"pro": "Expansions", "cut": "Cuts"}


def rate_table():
    """DataFrame indexed by year, columns (kind, age, iso3), log rate."""
    asfr = load_asfr()
    eurostat_isos = [c for c in asfr if c not in HFD_CODES and c not in ("AUS", "NZL", "URY")]
    src = {"all": asfr, "first": load_first(eurostat_isos)}
    cols = {(k, a, c): np.log(s) for k, d in src.items() for c, v in d.items() for a, s in v.items()}
    return pd.DataFrame(cols).sort_index()


def relative_paths(events, logs):
    rows = []
    for e in events.itertuples():
        for kind, age, name in ROWS:
            col = (kind, age, e.iso3)
            if col not in logs:
                continue
            block = logs.xs((kind, age), axis=1, level=(0, 1))
            base = e.year - 1
            if base not in block.index or pd.isna(block.at[base, e.iso3]) or e.year not in block.index \
                    or pd.isna(block.at[e.year, e.iso3]):
                continue
            for t in WINDOW:
                y = e.year + t
                if y not in block.index:
                    continue
                own = block.at[y, e.iso3] - block.at[base, e.iso3]
                others = (block.loc[y] - block.loc[base]).drop(e.iso3).dropna()
                if pd.isna(own) or others.empty:
                    continue
                rows.append(dict(iso3=e.iso3, country=COUNTRIES[e.iso3][0], year=e.year, domain=e.domain,
                                 direction=e.direction, description=e.description, row=name, t=t,
                                 diff=100 * (np.exp(own - others.mean()) - 1)))
    return pd.DataFrame(rows)


def domain_chart(d, domain):
    names = [r[2] for r in ROWS]
    fig = make_subplots(rows=1, cols=4, shared_yaxes=True, subplot_titles=names, horizontal_spacing=0.03)
    for j, name in enumerate(names, start=1):
        for direction in ("pro", "cut"):
            x = d[(d.row == name) & (d.direction == direction)]
            if x.empty:
                continue
            for (iso, yr), g in x.groupby(["iso3", "year"]):
                g = g.sort_values("t")
                fig.add_trace(go.Scatter(
                    x=g.t, y=g["diff"], mode="lines", line=dict(color=COLOR[direction], width=1), opacity=0.18,
                    hovertext=[f"{COUNTRIES[iso][0]} {yr}: {g.description.iloc[0]}<br>t={t:+d}: {v:+.1f}%"
                               for t, v in zip(g.t, g["diff"])],
                    hoverinfo="text", showlegend=False), row=1, col=j)
            m = x.groupby("t")["diff"].agg(["mean", "count"]).reset_index()
            fig.add_trace(go.Scatter(
                x=m.t, y=m["mean"], mode="lines+markers", line=dict(color=COLOR[direction], width=2.5),
                marker=dict(size=7), name=f"{NAME[direction]} (mean)", legendgroup=direction, showlegend=j == 1,
                hovertext=[f"{NAME[direction]}, t={t:+d}: {v:+.1f}% (n={n})" for t, v, n in zip(m.t, m["mean"], m["count"])],
                hoverinfo="text"), row=1, col=j)
        fig.add_vline(x=-0.5, line=dict(color="#9a9995", width=1, dash="dot"), row=1, col=j)
        fig.add_hline(y=0, line=dict(color="#9a9995", width=1), row=1, col=j)
    fig.update_xaxes(dtick=2, title_text="Years from change", gridcolor="#ecebe8")
    fig.update_yaxes(ticksuffix="%", gridcolor="#ecebe8", range=[-25, 25])
    fig.update_yaxes(title_text="vs year before, relative to other countries", row=1, col=1)
    fig.update_layout(template="plotly_white", height=380, hovermode="closest", title=None,
                      legend=dict(orientation="h", x=0, y=1.22), margin=dict(t=90, l=70, r=20, b=50))
    return fig


def main():
    events = load_events()
    events = events[events.domain.isin(DOMAINS) & events.direction.isin(["pro", "cut"])]
    d = relative_paths(events, rate_table())
    d.round(2).to_csv(OUTDIR / "policy_event_study.csv", index=False)
    summary = []
    for domain in DOMAINS:
        x = d[d.domain == domain]
        if x.empty:
            continue
        write_html(domain_chart(x, domain), OUTDIR / f"policy_event_study_{domain}.html")
        out = trend_breaks(x).groupby(["direction", "row"])["brk"].agg(
            ["mean", "median", "count", lambda v: (v > 0).mean()]).round(1)
        out.columns = ["mean", "median", "n", "share_up"]
        print(f"\n{DOMAINS[domain]}\n{out}")
        summary.append(out.reset_index().assign(domain=domain))
    pd.concat(summary).to_csv(OUTDIR / "policy_event_study_summary.csv", index=False)


def trend_breaks(d):
    """Per change and rate: slope over t = -1..4 minus slope over t = -4..-1 (points a year, relative
    to other countries); needs 3+ years on each side."""
    rows = []
    for (direction, row, iso, yr), g in d.groupby(["direction", "row", "iso3", "year"]):
        pre, post = g[g.t <= -1], g[g.t >= -1]
        if len(pre) < 3 or len(post) < 3:
            continue
        rows.append(dict(direction=direction, row=row, iso3=iso, year=yr,
                         brk=np.polyfit(post.t, post["diff"], 1)[0] - np.polyfit(pre.t, pre["diff"], 1)[0]))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    main()

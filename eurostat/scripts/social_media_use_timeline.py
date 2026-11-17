"""Social network participation among 16-24s beside fertility at ages 20-29, by country.

Eurostat isoc_ci_ac_i, indicator I_IUSNET (participated in social networks: created a user
profile or posted messages, last 3 months, % of individuals aged 16-24), 2011-2025;
Eurostat demo_frate (age-specific fertility rates). See young_fertility.py for download URLs.
"""

from timeline_chart import timeline
from young_fertility import OUTDIR, internet_use, write_html, young_fertility

if __name__ == "__main__":
    fig = timeline(internet_use("sn_slim.csv"), young_fertility(),
                   "Social network use, ages 16–24", "Social network use")
    write_html(fig, OUTDIR / "social_media_use_timeline.html")

"""Mobile internet use among 16-24s beside fertility at ages 20-29, by country.

Eurostat isoc_ci_im_i, indicator I_IUMP (use of a mobile phone or smartphone to access the
internet away from home or work, last 3 months, % of individuals aged 16-24), 2011-2019;
Eurostat demo_frate (age-specific fertility rates). See young_fertility.py for download URLs.
"""

from timeline_chart import timeline
from young_fertility import OUTDIR, internet_use, write_html, young_fertility

if __name__ == "__main__":
    fig = timeline(internet_use("imp_slim.csv"), young_fertility(),
                   "Mobile internet use, ages 16–24", "Mobile internet use")
    write_html(fig, OUTDIR / "smartphone_adoption_timeline.html")

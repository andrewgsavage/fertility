"""Rise in mobile internet use among 16-24s vs change in fertility at ages 20-29, 2011-2019.

Eurostat isoc_ci_im_i (I_IUMP) and demo_frate. See young_fertility.py for download URLs.
"""

from scatter_chart import changes, scatter
from young_fertility import OUTDIR, internet_use, write_html

Y0, Y1 = 2011, 2019

if __name__ == "__main__":
    rows = changes(internet_use("imp_slim.csv"), Y0, Y1)
    fig, r = scatter(rows, f"Change in mobile internet use, ages 16–24, {Y0}–{Y1}", "Mobile internet use", Y0, Y1)
    write_html(fig, OUTDIR / "smartphone_vs_young_fertility.html")
    print("r =", round(r, 3), "n =", len(rows))
    for x in sorted(rows, key=lambda z: z["du"]):
        print(x["country"], round(x["u0"]), round(x["u1"]), round(x["f0"], 3), round(x["f1"], 3), round(x["df"], 1))

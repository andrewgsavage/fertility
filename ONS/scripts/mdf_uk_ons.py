"""Period TMR, CPM and TFR for England & Wales, reconstructed from ONS cohort Table 3.
Prints them by year; the calculation lives in common/ons_mdf.py (shared with
HFD/scripts/mdf_facet.py).
"""

from common.ons_mdf import load_period_metrics

if __name__ == "__main__":
    metrics = load_period_metrics()
    for year in sorted(metrics):
        tmr, cpm, tfr = metrics[year]
        print(f"{year}: TMR={tmr:.3f} CPM={cpm:.3f} TFR={tfr:.3f}")

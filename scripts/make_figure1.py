"""Figure 1: monthly installed capacity, physical guarantee and generation of ACL-participating biomass plants.

Reads data/derived/biomassa_acl_monthly.csv (built by build_monthly_series.py) and writes
figures/Figure_1.pdf (vector) and figures/Figure_1.png (340 dpi, >= 2244 px full-page width).
Two stacked panels share the time axis instead of using two y-scales. Missing months stay as gaps.
"""
import pathlib

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
BLUE, ORANGE = "#2a78d6", "#eb6834"  # categorical slots 1 and 2 (validated default palette)
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#dedcd5"

d = pd.read_csv(ROOT / "data" / "derived" / "biomassa_acl_monthly.csv")
d["date"] = pd.PeriodIndex(d["month"], freq="M").to_timestamp()
full = pd.DataFrame({"date": pd.date_range(d["date"].min(), d["date"].max(), freq="MS")})
d = full.merge(d, on="date", how="left")  # reinserts missing months as NaN -> visible gaps

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED})
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.48, 5.6), sharex=True,
                             gridspec_kw={"height_ratios": [1, 1.4], "hspace": 0.12})

for ax in (a1, a2):
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for y in (2024, 2025, 2026):
        ax.axvline(pd.Timestamp(f"{y}-01-01"), color=MUTED, linewidth=0.7, linestyle=(0, (3, 3)), zorder=0)

a1.plot(d["date"], d["installed_capacity_MW"], color=BLUE, linewidth=2, drawstyle="steps-post")
a1.set_ylabel("Installed capacity (MW)")
a1.set_ylim(0, 17000)
a1.set_title("(a) Installed capacity", loc="left", fontsize=9, color=INK)

a2.plot(d["date"], d["physical_guarantee_MW"], color=BLUE, linewidth=2, drawstyle="steps-post",
        label="Physical guarantee (MW, as labelled)")
a2.plot(d["date"], d["generation_MWmed"], color=ORANGE, linewidth=2, marker="o", markersize=4,
        label="Generation (MWmed)")
a2.set_ylabel("MW / MWmed")
a2.set_ylim(0, 5000)
a2.set_title("(b) Physical guarantee and generation", loc="left", fontsize=9, color=INK)
a2.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="none", framealpha=1, fontsize=8, ncol=2)
last = d.dropna(subset=["generation_MWmed"]).iloc[-1]
a2.annotate("Guarantee", (d["date"].iloc[-1], d["physical_guarantee_MW"].iloc[-1]), xytext=(4, -12),
            textcoords="offset points", color=INK, fontsize=8)
a2.annotate("Generation", (last["date"], last["generation_MWmed"]), xytext=(4, 2),
            textcoords="offset points", color=INK, fontsize=8)

a2.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 4, 7, 10)))
a2.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
a2.set_xlim(d["date"].min() - pd.Timedelta(days=15), d["date"].max() + pd.Timedelta(days=75))

OUT.mkdir(exist_ok=True)
fig.savefig(OUT / "Figure_1.pdf", bbox_inches="tight")
fig.savefig(OUT / "Figure_1.png", dpi=340, bbox_inches="tight")
print("saved", OUT / "Figure_1.pdf", OUT / "Figure_1.png")

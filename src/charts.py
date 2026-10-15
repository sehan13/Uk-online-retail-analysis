"""
Charts for the report. One clear message per chart, one hue (blue) for
magnitude, a light-to-dark blue scale for heatmaps, recessive grid and axes,
and labels only where they help.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.ticker import FuncFormatter, PercentFormatter  # noqa: E402

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
BLUE = "#2a78d6"
BLUE_LIGHT = "#86b6ef"
BLUES = LinearSegmentedColormap.from_list(
    "blues", ["#f2f7fd", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"])

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.family": "DejaVu Sans", "font.size": 10,
    "axes.edgecolor": GRID, "axes.labelcolor": INK_2, "axes.titlecolor": INK,
    "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlepad": 26,
    "xtick.color": INK_2, "ytick.color": INK_2, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": False, "grid.color": GRID, "grid.linewidth": 0.8,
})

gbp_k = FuncFormatter(lambda v, _: f"£{v / 1e3:,.0f}k")
gbp_m = FuncFormatter(lambda v, _: f"£{v / 1e6:,.1f}m")


def _subtitle(ax, text):
    ax.text(0, 1.02, text, transform=ax.transAxes, fontsize=9.5, color=INK_2, va="bottom")


def _save(fig, out_dir, name):
    path = Path(out_dir) / name
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return path


def monthly_revenue_chart(monthly, out_dir):
    fig, ax = plt.subplots(figsize=(9, 4.2))
    x = range(len(monthly))
    labels = [p.strftime("%b\n%Y") if p.month in (12, 1) else p.strftime("%b") for p in monthly.index]
    ax.plot(x, monthly["revenue"], color=BLUE, linewidth=2, marker="o", markersize=5)
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_xticks(list(x), labels)
    ax.yaxis.set_major_formatter(gbp_k)
    ax.set_ylim(0, monthly["revenue"].max() * 1.15)
    peak = monthly["revenue"].idxmax()
    i = list(monthly.index).index(peak)
    ax.annotate(f"£{monthly['revenue'].max() / 1e6:.2f}m in {peak.strftime('%B')}",
                (i, monthly["revenue"].max()), xytext=(-10, 10), textcoords="offset points",
                ha="right", color=INK, fontsize=9.5, fontweight="bold")
    ax.set_title("Monthly revenue nearly doubled from summer to November")
    _subtitle(ax, "Revenue by month, Dec 2010 – Nov 2011 (Dec 2011 excluded as a partial month)")
    return _save(fig, out_dir, "monthly_revenue.png")


def _hbar(ax, labels, values, fmt, highlight_first=False):
    y = range(len(values))[::-1]
    colors = [BLUE] * len(values)
    ax.barh(list(y), values, color=colors, height=0.62)
    ax.set_yticks(list(y), labels)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.set_xticks([])
    for yi, v in zip(y, values):
        ax.text(v, yi, "  " + fmt(v), va="center", fontsize=9, color=INK_2)
    ax.set_xlim(0, max(values) * 1.18)


def countries_chart(countries, uk_share, out_dir):
    fig, ax = plt.subplots(figsize=(8, 4.6))
    _hbar(ax, countries.index, countries["revenue"], lambda v: f"£{v / 1e3:,.0f}k")
    ax.set_title("Outside the UK, a few large trade buyers drive revenue")
    _subtitle(ax, f"Top 10 international markets by revenue (the UK itself is {uk_share:.0%} of all revenue)")
    return _save(fig, out_dir, "top_international_markets.png")


def products_chart(products, out_dir):
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    labels = [d.title().replace("'S ", "'s ") for d in products.index]
    _hbar(ax, labels, products["revenue"], lambda v: f"£{v / 1e3:,.0f}k")
    ax.set_title("Top 10 products by revenue")
    _subtitle(ax, "Home décor and gift items lead; the cake stand alone made £170k")
    return _save(fig, out_dir, "top_products.png")


def segments_chart(summary, out_dir):
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    s = summary.sort_values("revenue_share", ascending=False)
    labels = [f"{seg}  ({c:.0%} of customers)" for seg, c in zip(s.index, s["customer_share"])]
    _hbar(ax, labels, s["revenue_share"], lambda v: f"{v:.0%} of revenue")
    ax.set_title("A quarter of customers (Champions) bring in two-thirds of revenue")
    _subtitle(ax, "Share of revenue by RFM customer segment")
    return _save(fig, out_dir, "rfm_segments.png")


def heatmap_weekday_hour(table, out_dir):
    fig, ax = plt.subplots(figsize=(9, 3.6))
    im = ax.imshow(table.values, cmap=BLUES, aspect="auto")
    ax.set_xticks(range(len(table.columns)), [f"{h}:00" for h in table.columns], rotation=0)
    ax.set_yticks(range(len(table.index)), table.index)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=8, colors=INK_2, length=0)
    cb.set_label("Orders", color=INK_2, fontsize=9)
    ax.set_title("Orders peak at midday on weekdays; no orders on Saturdays")
    _subtitle(ax, "Number of orders by day of week and hour placed")
    return _save(fig, out_dir, "orders_by_day_hour.png")


def cohort_chart(retention, out_dir):
    r = retention.iloc[:, 1:].dropna(how="all")      # month 0 is always 100%; drop cohorts with no follow-up yet
    fig, ax = plt.subplots(figsize=(9, 5))
    im = ax.imshow(r.values, cmap=BLUES, aspect="auto", vmin=0, vmax=0.5)
    ax.set_xticks(range(r.shape[1]), [str(c) for c in r.columns])
    ax.set_yticks(range(r.shape[0]), [p.strftime("%b %Y") for p in r.index])
    ax.set_xlabel("Months after first purchase")
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    for (i, j), v in __import__("numpy").ndenumerate(r.values):
        if v == v:  # not NaN
            ax.text(j, i, f"{v:.0%}", ha="center", va="center", fontsize=7.5,
                    color="white" if v > 0.3 else INK)
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02, format=PercentFormatter(1.0))
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=8, colors=INK_2, length=0)
    ax.set_title("The first cohort (Dec 2010) stays far more loyal than later ones")
    _subtitle(ax, "% of each monthly customer cohort that ordered again N months later")
    return _save(fig, out_dir, "cohort_retention.png")

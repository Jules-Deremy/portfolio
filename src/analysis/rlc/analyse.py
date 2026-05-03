"""
RLC Token Analysis — Visualization Script
Generates interactive Plotly charts from Dune data
and exports them as HTML files for portfolio integration.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ── Config ───────────────────────────────────────────────
DATA_DIR = "data"
OUTPUT_DIR = "charts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEAL      = "#0D9488"
TEAL_DARK = "#0F766E"
GRAY      = "#6B7280"
GRID      = "#E5E7EB"

# ── Load data ─────────────────────────────────────────────

def load(filename):
    path = os.path.join(DATA_DIR, filename)
    df = pd.read_csv(path)
    print(f"Loaded {filename}: {len(df)} rows")
    return df

monthly   = load("rlc_monthly_activity.csv")
daily     = load("rlc_daily_activity.csv")
dex       = load("rlc_dex_activity.csv")
august    = load("rlc_august_peak.csv")
march     = load("rlc_march_peak.csv")
receivers = load("rlc_top_receivers.csv")

# ── Parse dates ───────────────────────────────────────────

monthly["month"] = pd.to_datetime(monthly["month"])
daily["day"]     = pd.to_datetime(daily["day"])
dex["month"]     = pd.to_datetime(dex["month"])
august["day"]    = pd.to_datetime(august["day"])
march["day"]     = pd.to_datetime(march["day"])

monthly = monthly.sort_values("month")
daily   = daily.sort_values("day")
dex     = dex.sort_values("month")
august  = august.sort_values("day")
march   = march.sort_values("day")

print("\nData loaded successfully.\n")

# ── Chart 1 — Monthly transfer activity ──────────────────

fig1 = make_subplots(specs=[[{"secondary_y": True}]])

fig1.add_trace(go.Bar(
    x=monthly["month"],
    y=monthly["nb_transfers"],
    name="Transfers",
    marker_color=TEAL,
    marker_line_width=0,
    opacity=0.9,
), secondary_y=False)

fig1.add_trace(go.Scatter(
    x=monthly["month"],
    y=monthly["unique_senders"],
    name="Unique senders",
    mode="lines+markers",
    line=dict(color=TEAL_DARK, width=2),
    marker=dict(size=6, color=TEAL_DARK),
), secondary_y=True)

fig1.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Inter, sans-serif", color="#1E3A2E", size=13),
    margin=dict(t=60, b=60, l=60, r=40),
    title=dict(text="RLC Monthly Transfer Activity", font=dict(size=18)),
    xaxis=dict(showgrid=False, linecolor=GRID, linewidth=1),
    yaxis=dict(title="Number of transfers", gridcolor=GRID),
    yaxis2=dict(title="Unique senders", showgrid=False),
    legend=dict(orientation="h", y=-0.2),
    barmode="overlay",
)

fig1.write_html(f"{OUTPUT_DIR}/chart1_monthly_activity.html")
print("Chart 1 saved.")

# ── Chart 2 — DEX trading volume ─────────────────────────

fig2 = make_subplots(specs=[[{"secondary_y": True}]])

fig2.add_trace(go.Bar(
    x=dex["month"],
    y=dex["volume_usd"],
    name="Volume USD",
    marker_color=TEAL,
    marker_line_width=0,
    opacity=0.9,
), secondary_y=False)

fig2.add_trace(go.Scatter(
    x=dex["month"],
    y=dex["nb_swaps"],
    name="Number of swaps",
    mode="lines+markers",
    line=dict(color=TEAL_DARK, width=2),
    marker=dict(size=6, color=TEAL_DARK),
), secondary_y=True)

fig2.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Inter, sans-serif", color="#1E3A2E", size=13),
    margin=dict(t=60, b=60, l=60, r=40),
    title=dict(text="RLC DEX Trading Activity (Uniswap)", font=dict(size=18)),
    xaxis=dict(showgrid=False, linecolor=GRID, linewidth=1),
    yaxis=dict(title="Volume USD", gridcolor=GRID),
    yaxis2=dict(title="Number of swaps", showgrid=False),
    legend=dict(orientation="h", y=-0.2),
)

fig2.write_html(f"{OUTPUT_DIR}/chart2_dex_activity.html")
print("Chart 2 saved.")

# ── Chart 3 — August 2025 peak ───────────────────────────

fig3 = make_subplots(
    rows=2, cols=1,
    subplot_titles=("Daily transfers — July to September 2025", "Daily volume RLC"),
    vertical_spacing=0.15,
)

fig3.add_trace(go.Bar(
    x=august["day"],
    y=august["nb_transfers"],
    name="Transfers",
    marker_color=TEAL,
    marker_line_width=0,
), row=1, col=1)

fig3.add_trace(go.Bar(
    x=august["day"],
    y=august["volume_rlc"],
    name="Volume RLC",
    marker_color=TEAL_DARK,
    marker_line_width=0,
), row=2, col=1)

fig3.add_vline(
    x=pd.Timestamp("2025-08-28").timestamp() * 1000,
    line_dash="dash",
    line_color=GRAY,
    annotation_text="Guotai Junan listing",
    annotation_position="top right",
    annotation_font_color=GRAY,
)

fig3.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Inter, sans-serif", color="#1E3A2E", size=13),
    margin=dict(t=60, b=60, l=60, r=40),
    title=dict(text="August 2025 — Institutional Spike", font=dict(size=18)),
    showlegend=False,
    height=500,
)
fig3.update_xaxes(showgrid=False, linecolor=GRID)
fig3.update_yaxes(gridcolor=GRID)

fig3.write_html(f"{OUTPUT_DIR}/chart3_august_peak.html")
print("Chart 3 saved.")

# ── Chart 4 — March 2025 peak ────────────────────────────

fig4 = make_subplots(
    rows=2, cols=1,
    subplot_titles=("Daily transfers — March to May 2025", "Daily volume RLC"),
    vertical_spacing=0.15,
)

fig4.add_trace(go.Bar(
    x=march["day"],
    y=march["nb_transfers"],
    name="Transfers",
    marker_color=TEAL,
    marker_line_width=0,
), row=1, col=1)

fig4.add_trace(go.Bar(
    x=march["day"],
    y=march["volume_rlc"],
    name="Volume RLC",
    marker_color=TEAL_DARK,
    marker_line_width=0,
), row=2, col=1)

fig4.add_vline(
    x=pd.Timestamp("2025-03-12").timestamp() * 1000,
    line_dash="dash",
    line_color=GRAY,
    annotation_text="AMA Trusted AI (Mar 12)",
    annotation_position="top left",
    annotation_font_color=GRAY,
    annotation_font_size=11,
)

fig4.add_vline(
    x=pd.Timestamp("2025-03-17").timestamp() * 1000,
    line_dash="dot",
    line_color=TEAL,
    annotation_text="Peak (Mar 17)",
    annotation_position="bottom right",
    annotation_font_color=TEAL,
    annotation_font_size=11,
)

fig4.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Inter, sans-serif", color="#1E3A2E", size=13),
    margin=dict(t=60, b=60, l=60, r=40),
    title=dict(text="March 2025 — Community Activation", font=dict(size=18)),
    showlegend=False,
    height=500,
)
fig4.update_xaxes(showgrid=False, linecolor=GRID)
fig4.update_yaxes(gridcolor=GRID)

fig4.write_html(f"{OUTPUT_DIR}/chart4_march_peak.html")
print("Chart 4 saved.")

# ── Chart 5 — Top receivers ───────────────────────────────

top10 = receivers.head(10).copy()
top10["address_short"] = top10["address"].str[:6] + "..." + top10["address"].str[-4:]
top10 = top10.sort_values("volume_received_rlc")

fig5 = go.Figure(go.Bar(
    x=top10["volume_received_rlc"],
    y=top10["address_short"],
    orientation="h",
    marker_color=TEAL,
    marker_line_width=0,
    text=top10["volume_received_rlc"].apply(lambda x: f"{x/1e6:.1f}M RLC"),
    textposition="outside",
))

fig5.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Inter, sans-serif", color="#1E3A2E", size=13),
    margin=dict(t=60, b=60, l=80, r=80),
    title=dict(text="Top 10 RLC Receivers — Last 12 Months", font=dict(size=18)),
    xaxis=dict(title="Volume received (RLC)", showgrid=True, gridcolor=GRID),
    yaxis=dict(showgrid=False),
    height=420,
)

fig5.write_html(f"{OUTPUT_DIR}/chart5_top_receivers.html")
print("Chart 5 saved.")

# ── Summary stats ─────────────────────────────────────────

print("\n" + "=" * 50)
print("Key Stats")
print("=" * 50)
print(f"Total transfers (12m):      {monthly['nb_transfers'].sum():,.0f}")
print(f"Total volume RLC (12m):     {monthly['volume_rlc'].sum()/1e6:.1f}M RLC")
print(f"Total DEX volume USD (12m): ${dex['volume_usd'].sum()/1e6:.2f}M")
print(f"Peak month (transfers):     {monthly.loc[monthly['nb_transfers'].idxmax(), 'month'].strftime('%B %Y')}")
print(f"\nAll charts saved in ./{OUTPUT_DIR}/")
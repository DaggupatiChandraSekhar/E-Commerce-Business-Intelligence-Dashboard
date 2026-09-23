"""
E-Commerce Business Intelligence Dashboard
=========================================
Dataset : global_ecommerce_sales.csv
Framework: Streamlit + Plotly + Pandas
"""

import os
import warnings

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ---------- global ---------- */
    [data-testid="stAppViewContainer"] {background-color: #f0f2f6;}
    [data-testid="stSidebar"]          {background-color: #1e293b;}
    [data-testid="stSidebar"] * {color: #e2e8f0 !important;}
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stDateInput label {color: #94a3b8 !important; font-size:0.75rem !important;}

    /* ---------- KPI cards ---------- */
    .kpi-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 18px 20px 14px 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,.08);
        border-left: 4px solid #3b82f6;
        height: 115px;
    }
    .kpi-card.green  {border-left-color: #22c55e;}
    .kpi-card.amber  {border-left-color: #f59e0b;}
    .kpi-card.violet {border-left-color: #8b5cf6;}
    .kpi-card.rose   {border-left-color: #f43f5e;}
    .kpi-card.teal   {border-left-color: #14b8a6;}

    .kpi-label {font-size: 0.72rem; color:#64748b; font-weight:600;
                text-transform:uppercase; letter-spacing:.06em; margin-bottom:4px;}
    .kpi-value {font-size: 1.6rem; font-weight:700; color:#0f172a; line-height:1.15;}
    .kpi-delta {font-size: 0.75rem; color:#64748b; margin-top:4px;}

    /* ---------- section headers ---------- */
    .section-header {
        font-size: 1.05rem; font-weight: 700; color: #1e293b;
        border-bottom: 2px solid #3b82f6; padding-bottom: 5px;
        margin: 24px 0 14px 0;
    }
    .section-sub {font-size: 0.82rem; color:#64748b; margin-top:-10px; margin-bottom:14px;}

    /* ---------- insight box ---------- */
    .insight-box {
        background:#eff6ff; border:1px solid #bfdbfe;
        border-radius:8px; padding:14px 18px; margin:6px 0;
        font-size:0.84rem; color:#1e3a5f; line-height:1.55;
    }
    .insight-box.warn {background:#fefce8; border-color:#fde68a; color:#713f12;}
    .insight-box.risk {background:#fef2f2; border-color:#fecaca; color:#7f1d1d;}
    .insight-box.opp  {background:#f0fdf4; border-color:#bbf7d0; color:#14532d;}

    h1 {color:#0f172a !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Load data ─────────────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "global_ecommerce_sales.csv")


@st.cache_data(show_spinner="Loading dataset…")
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Normalise column names (strip whitespace)
    df.columns = df.columns.str.strip()

    # Parse dates
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")

    # Ensure numeric types
    for col in ["Quantity", "Unit_Price", "Discount_Percent",
                "Total_Sales", "Shipping_Cost", "Profit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with missing dates (unfilterable)
    df = df.dropna(subset=["Order_Date"])

    # Derived fields
    df["Year"]        = df["Order_Date"].dt.year
    df["Month"]       = df["Order_Date"].dt.to_period("M").astype(str)
    df["YearMonth"]   = df["Order_Date"].dt.to_period("M")   # sortable

    return df


df_raw = load_data(DATA_PATH)

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔎 Filters")
    st.markdown("---")

    # Date range
    min_date = df_raw["Order_Date"].min().date()
    max_date = df_raw["Order_Date"].max().date()
    date_range = st.date_input(
        "Order Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # Region
    all_regions = sorted(df_raw["Region"].dropna().unique())
    sel_regions = st.multiselect("Region", all_regions, default=all_regions)

    # Country
    all_countries = sorted(df_raw["Country"].dropna().unique())
    sel_countries = st.multiselect("Country", all_countries, default=all_countries)

    # Product Category
    all_cats = sorted(df_raw["Product_Category"].dropna().unique())
    sel_cats = st.multiselect("Product Category", all_cats, default=all_cats)

    # Customer Segment
    all_segs = sorted(df_raw["Customer_Segment"].dropna().unique())
    sel_segs = st.multiselect("Customer Segment", all_segs, default=all_segs)

    # Payment Method
    all_pmts = sorted(df_raw["Payment_Method"].dropna().unique())
    sel_pmts = st.multiselect("Payment Method", all_pmts, default=all_pmts)

    st.markdown("---")
    st.caption("E-Commerce BI Dashboard · v1.0")

# ── Apply filters ─────────────────────────────────────────────────────────────
if len(date_range) == 2:
    start_dt, end_dt = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_dt, end_dt = df_raw["Order_Date"].min(), df_raw["Order_Date"].max()

df = df_raw[
    (df_raw["Order_Date"] >= start_dt)
    & (df_raw["Order_Date"] <= end_dt)
    & (df_raw["Region"].isin(sel_regions))
    & (df_raw["Country"].isin(sel_countries))
    & (df_raw["Product_Category"].isin(sel_cats))
    & (df_raw["Customer_Segment"].isin(sel_segs))
    & (df_raw["Payment_Method"].isin(sel_pmts))
].copy()

# ── Guard: empty dataset ──────────────────────────────────────────────────────
if df.empty:
    st.warning("⚠️ No data matches the current filters. Please adjust your selections.")
    st.stop()

# ── Helper colours ────────────────────────────────────────────────────────────
PALETTE   = px.colors.qualitative.Safe
CLR_BLUE  = "#3b82f6"
CLR_GREEN = "#22c55e"
CLR_RED   = "#ef4444"
CLR_AMB   = "#f59e0b"


def fmt_currency(v: float) -> str:
    if v >= 1_000_000:
        return f"${v/1_000_000:.2f}M"
    if v >= 1_000:
        return f"${v/1_000:.1f}K"
    return f"${v:.2f}"


def plotly_defaults(fig, height: int = 350):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Segoe UI, system-ui, sans-serif", size=12, color="#374151"),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# TITLE
# ═══════════════════════════════════════════════════════════════════════════════
st.title("📊 E-Commerce Business Intelligence Dashboard")
st.markdown(
    f"Showing **{len(df):,}** orders · "
    f"{start_dt.strftime('%d %b %Y')} → {end_dt.strftime('%d %b %Y')}"
)

# ═══════════════════════════════════════════════════════════════════════════════
# 1 · KPIs
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">① KEY PERFORMANCE INDICATORS</div>', unsafe_allow_html=True)

total_sales    = df["Total_Sales"].sum()
total_profit   = df["Profit"].sum()
total_orders   = df["Order_ID"].nunique()
total_qty      = int(df["Quantity"].sum())
avg_order_val  = total_sales / total_orders if total_orders else 0
profit_margin  = (total_profit / total_sales * 100) if total_sales else 0

kpi_cols = st.columns(6)

kpi_data = [
    ("Total Sales",          fmt_currency(total_sales),         "kpi-card",         "Revenue from all orders"),
    ("Total Profit",         fmt_currency(total_profit),        "kpi-card green",    "Net profit across all orders"),
    ("Total Orders",         f"{total_orders:,}",               "kpi-card amber",    "Unique order count"),
    ("Total Qty Sold",       f"{total_qty:,}",                  "kpi-card violet",   "Units shipped"),
    ("Avg Order Value",      fmt_currency(avg_order_val),        "kpi-card rose",     "Revenue per order"),
    ("Profit Margin",        f"{profit_margin:.1f}%",           "kpi-card teal",     "Profit as % of sales"),
]

for col, (label, value, css, subtitle) in zip(kpi_cols, kpi_data):
    with col:
        st.markdown(
            f'<div class="{css}">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-delta">{subtitle}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ═══════════════════════════════════════════════════════════════════════════════
# 2 · TRENDS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">② TRENDS — WHERE ARE WE HEADING?</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Monthly Sales, Profit and Order Volume over time.</div>', unsafe_allow_html=True)

monthly = (
    df.groupby("YearMonth", sort=True)
    .agg(
        Sales=("Total_Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order_ID", "nunique"),
    )
    .reset_index()
)
monthly["Month_Label"] = monthly["YearMonth"].astype(str)
monthly["Profit_Margin_%"] = (monthly["Profit"] / monthly["Sales"] * 100).round(1)

t1, t2 = st.columns(2)

with t1:
    fig_trend_sp = go.Figure()
    fig_trend_sp.add_trace(go.Scatter(
        x=monthly["Month_Label"], y=monthly["Sales"],
        name="Sales", mode="lines+markers",
        line=dict(color=CLR_BLUE, width=2.5),
        marker=dict(size=5),
    ))
    fig_trend_sp.add_trace(go.Scatter(
        x=monthly["Month_Label"], y=monthly["Profit"],
        name="Profit", mode="lines+markers",
        line=dict(color=CLR_GREEN, width=2.5, dash="dot"),
        marker=dict(size=5),
    ))
    fig_trend_sp.update_layout(title="Monthly Sales vs Profit ($)")
    plotly_defaults(fig_trend_sp)
    fig_trend_sp.update_xaxes(tickangle=-45, nticks=18)
    st.plotly_chart(fig_trend_sp, use_container_width=True)

with t2:
    fig_orders = go.Figure()
    fig_orders.add_trace(go.Bar(
        x=monthly["Month_Label"], y=monthly["Orders"],
        name="Orders", marker_color=CLR_AMB,
    ))
    fig_orders.add_trace(go.Scatter(
        x=monthly["Month_Label"], y=monthly["Profit_Margin_%"],
        name="Profit Margin %", mode="lines+markers",
        line=dict(color=CLR_RED, width=2.5),
        yaxis="y2",
    ))
    fig_orders.update_layout(
        title="Monthly Order Volume & Profit Margin %",
        yaxis2=dict(
            title="Profit Margin %",
            overlaying="y", side="right",
            showgrid=False, zeroline=False,
            ticksuffix="%",
        ),
    )
    plotly_defaults(fig_orders)
    fig_orders.update_xaxes(tickangle=-45, nticks=18)
    st.plotly_chart(fig_orders, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 3 · DRIVERS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">③ PERFORMANCE DRIVERS — WHY IS PERFORMANCE CHANGING?</div>', unsafe_allow_html=True)

# ── 3a · Region & Country ─────────────────────────────────────────────────────
d1, d2 = st.columns(2)

region_grp = (
    df.groupby("Region")
    .agg(Sales=("Total_Sales", "sum"), Profit=("Profit", "sum"))
    .reset_index()
    .sort_values("Sales", ascending=True)
)
region_grp["Margin_%"] = (region_grp["Profit"] / region_grp["Sales"] * 100).round(1)

with d1:
    fig_region = go.Figure()
    fig_region.add_trace(go.Bar(
        y=region_grp["Region"], x=region_grp["Sales"],
        name="Sales", orientation="h", marker_color=CLR_BLUE,
    ))
    fig_region.add_trace(go.Bar(
        y=region_grp["Region"], x=region_grp["Profit"],
        name="Profit", orientation="h", marker_color=CLR_GREEN,
    ))
    fig_region.update_layout(title="Sales & Profit by Region", barmode="group")
    plotly_defaults(fig_region, height=320)
    st.plotly_chart(fig_region, use_container_width=True)

country_grp = (
    df.groupby("Country")
    .agg(Sales=("Total_Sales", "sum"), Profit=("Profit", "sum"))
    .reset_index()
    .sort_values("Sales", ascending=False)
    .head(15)
    .sort_values("Sales", ascending=True)
)

with d2:
    fig_country = go.Figure()
    fig_country.add_trace(go.Bar(
        y=country_grp["Country"], x=country_grp["Sales"],
        name="Sales", orientation="h", marker_color="#6366f1",
    ))
    fig_country.add_trace(go.Bar(
        y=country_grp["Country"], x=country_grp["Profit"],
        name="Profit", orientation="h", marker_color="#a5f3fc",
    ))
    fig_country.update_layout(
        title="Top 15 Countries by Sales", barmode="group",
        yaxis=dict(autorange="reversed"),
    )
    plotly_defaults(fig_country, height=320)
    st.plotly_chart(fig_country, use_container_width=True)

# ── 3b · Product Category ─────────────────────────────────────────────────────
d3, d4 = st.columns(2)

cat_grp = (
    df.groupby("Product_Category")
    .agg(Sales=("Total_Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order_ID", "nunique"))
    .reset_index()
)
cat_grp["Margin_%"] = (cat_grp["Profit"] / cat_grp["Sales"] * 100).round(1)

with d3:
    fig_cat = px.bar(
        cat_grp.sort_values("Sales", ascending=False),
        x="Product_Category", y=["Sales", "Profit"],
        barmode="group",
        title="Sales & Profit by Product Category",
        color_discrete_sequence=[CLR_BLUE, CLR_GREEN],
        labels={"value": "$", "variable": "Metric"},
    )
    plotly_defaults(fig_cat, height=320)
    st.plotly_chart(fig_cat, use_container_width=True)

with d4:
    fig_cat_margin = px.bar(
        cat_grp.sort_values("Margin_%", ascending=False),
        x="Product_Category", y="Margin_%",
        title="Profit Margin % by Category",
        color="Margin_%",
        color_continuous_scale=["#ef4444", "#f59e0b", "#22c55e"],
        text="Margin_%",
    )
    fig_cat_margin.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_cat_margin.update_coloraxes(showscale=False)
    plotly_defaults(fig_cat_margin, height=320)
    st.plotly_chart(fig_cat_margin, use_container_width=True)

# ── 3c · Top Products ─────────────────────────────────────────────────────────
d5, d6 = st.columns(2)

prod_grp = (
    df.groupby("Product_Name")
    .agg(Sales=("Total_Sales", "sum"), Profit=("Profit", "sum"))
    .reset_index()
)

with d5:
    top_sales = prod_grp.nlargest(10, "Sales").sort_values("Sales", ascending=True)
    fig_top_s = px.bar(
        top_sales, y="Product_Name", x="Sales",
        orientation="h", title="Top 10 Products by Sales",
        color="Sales", color_continuous_scale=["#bfdbfe", CLR_BLUE],
        text="Sales",
    )
    fig_top_s.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig_top_s.update_coloraxes(showscale=False)
    plotly_defaults(fig_top_s, height=340)
    st.plotly_chart(fig_top_s, use_container_width=True)

with d6:
    top_profit = prod_grp.nlargest(10, "Profit").sort_values("Profit", ascending=True)
    fig_top_p = px.bar(
        top_profit, y="Product_Name", x="Profit",
        orientation="h", title="Top 10 Products by Profit",
        color="Profit", color_continuous_scale=["#bbf7d0", CLR_GREEN],
        text="Profit",
    )
    fig_top_p.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig_top_p.update_coloraxes(showscale=False)
    plotly_defaults(fig_top_p, height=340)
    st.plotly_chart(fig_top_p, use_container_width=True)

# ── 3d · Customer Segment & Payment Method ───────────────────────────────────
d7, d8 = st.columns(2)

seg_grp = (
    df.groupby("Customer_Segment")
    .agg(Sales=("Total_Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order_ID", "nunique"))
    .reset_index()
)
seg_grp["Margin_%"] = (seg_grp["Profit"] / seg_grp["Sales"] * 100).round(1)
seg_grp["AOV"] = seg_grp["Sales"] / seg_grp["Orders"]

with d7:
    fig_seg = go.Figure()
    fig_seg.add_trace(go.Bar(
        x=seg_grp["Customer_Segment"], y=seg_grp["Sales"],
        name="Sales", marker_color=CLR_BLUE,
    ))
    fig_seg.add_trace(go.Bar(
        x=seg_grp["Customer_Segment"], y=seg_grp["Profit"],
        name="Profit", marker_color=CLR_GREEN,
    ))
    fig_seg.add_trace(go.Scatter(
        x=seg_grp["Customer_Segment"], y=seg_grp["Margin_%"],
        name="Margin %", mode="markers+lines",
        marker=dict(size=10, color=CLR_RED),
        yaxis="y2",
    ))
    fig_seg.update_layout(
        title="Customer Segment Performance",
        barmode="group",
        yaxis2=dict(
            title="Profit Margin %", overlaying="y",
            side="right", showgrid=False, ticksuffix="%",
        ),
    )
    plotly_defaults(fig_seg, height=320)
    st.plotly_chart(fig_seg, use_container_width=True)

pmt_grp = (
    df.groupby("Payment_Method")
    .agg(Sales=("Total_Sales", "sum"), Orders=("Order_ID", "nunique"))
    .reset_index()
)
pmt_grp["Share_%"] = (pmt_grp["Sales"] / pmt_grp["Sales"].sum() * 100).round(1)

with d8:
    fig_pmt = px.pie(
        pmt_grp, names="Payment_Method", values="Sales",
        title="Sales Share by Payment Method",
        color_discrete_sequence=PALETTE,
        hole=0.42,
    )
    fig_pmt.update_traces(texttemplate="%{label}<br>%{percent:.1%}", textposition="outside")
    plotly_defaults(fig_pmt, height=320)
    st.plotly_chart(fig_pmt, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 4 · RISKS & OPPORTUNITIES
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">④ RISKS & OPPORTUNITIES</div>', unsafe_allow_html=True)

# ── 4a · Discount vs Profitability ────────────────────────────────────────────
r1, r2 = st.columns(2)

disc_bins = pd.cut(df["Discount_Percent"], bins=[-1, 0, 5, 10, 20, 30], labels=["0%", "1-5%", "6-10%", "11-20%", "21-30%"])
disc_grp = (
    df.assign(Discount_Band=disc_bins)
    .groupby("Discount_Band", observed=True)
    .agg(
        Sales=("Total_Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order_ID", "nunique"),
    )
    .reset_index()
)
disc_grp["Margin_%"] = (disc_grp["Profit"] / disc_grp["Sales"] * 100).round(1)

with r1:
    fig_disc = go.Figure()
    fig_disc.add_trace(go.Bar(
        x=disc_grp["Discount_Band"].astype(str),
        y=disc_grp["Profit"],
        name="Total Profit ($)",
        marker_color=CLR_GREEN,
    ))
    fig_disc.add_trace(go.Scatter(
        x=disc_grp["Discount_Band"].astype(str),
        y=disc_grp["Margin_%"],
        name="Profit Margin %",
        mode="lines+markers",
        marker=dict(size=9, color=CLR_RED),
        yaxis="y2",
    ))
    fig_disc.update_layout(
        title="Discount Level vs Profit & Margin",
        yaxis2=dict(
            title="Margin %", overlaying="y",
            side="right", showgrid=False, ticksuffix="%",
        ),
    )
    plotly_defaults(fig_disc, height=330)
    st.plotly_chart(fig_disc, use_container_width=True)

# ── 4b · Shipping Cost by Region & Category ──────────────────────────────────
ship_grp = (
    df.groupby(["Region", "Product_Category"])
    .agg(Shipping=("Shipping_Cost", "sum"), Sales=("Total_Sales", "sum"))
    .reset_index()
)
ship_grp["Ship_to_Sales_%"] = (ship_grp["Shipping"] / ship_grp["Sales"] * 100).round(2)

with r2:
    fig_ship = px.bar(
        ship_grp,
        x="Region", y="Shipping",
        color="Product_Category",
        title="Total Shipping Cost by Region & Category",
        barmode="stack",
        color_discrete_sequence=PALETTE,
        labels={"Shipping": "Shipping Cost ($)"},
    )
    plotly_defaults(fig_ship, height=330)
    st.plotly_chart(fig_ship, use_container_width=True)

# ── 4c · Low-margin products (bottom 15 by margin) ───────────────────────────
r3, r4 = st.columns(2)

prod_risk = (
    df.groupby("Product_Name")
    .agg(Sales=("Total_Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order_ID", "nunique"))
    .reset_index()
)
prod_risk["Margin_%"] = (prod_risk["Profit"] / prod_risk["Sales"] * 100).round(1)

low_margin = prod_risk[prod_risk["Sales"] > prod_risk["Sales"].quantile(0.25)].nsmallest(15, "Margin_%")

with r3:
    fig_low = px.bar(
        low_margin.sort_values("Margin_%"),
        x="Margin_%", y="Product_Name",
        orientation="h",
        title="⚠️ Lowest-Margin Products (above 25th pct sales)",
        color="Margin_%",
        color_continuous_scale=["#ef4444", "#f59e0b", "#fde68a"],
        text="Margin_%",
    )
    fig_low.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_low.update_coloraxes(showscale=False)
    plotly_defaults(fig_low, height=380)
    st.plotly_chart(fig_low, use_container_width=True)

# ── 4d · High-sales / low-profit scatter (product level) ─────────────────────
with r4:
    # Annotate quadrants
    med_sales  = prod_risk["Sales"].median()
    med_margin = prod_risk["Margin_%"].median()

    fig_scatter = px.scatter(
        prod_risk,
        x="Sales", y="Margin_%",
        size="Orders",
        color="Margin_%",
        color_continuous_scale=["#ef4444", "#f59e0b", "#22c55e"],
        hover_name="Product_Name",
        hover_data={"Sales": ":,.0f", "Margin_%": ":.1f", "Orders": True},
        title="Sales vs Profit Margin (bubble = order count)",
        labels={"Sales": "Total Sales ($)", "Margin_%": "Profit Margin %"},
    )
    # Quadrant lines
    fig_scatter.add_vline(x=med_sales,  line_dash="dot", line_color="#94a3b8", line_width=1)
    fig_scatter.add_hline(y=med_margin, line_dash="dot", line_color="#94a3b8", line_width=1)
    fig_scatter.add_annotation(x=med_sales * 1.4, y=med_margin * 0.4,
                                text="⚠️ High sales,\nLow margin",
                                showarrow=False, font=dict(color="#dc2626", size=10))
    fig_scatter.update_coloraxes(showscale=False)
    plotly_defaults(fig_scatter, height=380)
    st.plotly_chart(fig_scatter, use_container_width=True)

# ── 4e · Shipping cost as % of sales by country ──────────────────────────────
r5, r6 = st.columns(2)

country_ship = (
    df.groupby("Country")
    .agg(Sales=("Total_Sales", "sum"), Shipping=("Shipping_Cost", "sum"), Profit=("Profit", "sum"))
    .reset_index()
)
country_ship["Ship_%_Sales"] = (country_ship["Shipping"] / country_ship["Sales"] * 100).round(2)
country_ship["Margin_%"]     = (country_ship["Profit"] / country_ship["Sales"] * 100).round(1)
high_ship = country_ship.nlargest(10, "Ship_%_Sales")

with r5:
    fig_cship = px.bar(
        high_ship.sort_values("Ship_%_Sales"),
        x="Ship_%_Sales", y="Country",
        orientation="h",
        title="Countries with Highest Shipping Cost (% of Sales)",
        color="Ship_%_Sales",
        color_continuous_scale=["#fde68a", "#f59e0b", "#ef4444"],
        text="Ship_%_Sales",
    )
    fig_cship.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_cship.update_coloraxes(showscale=False)
    plotly_defaults(fig_cship, height=340)
    st.plotly_chart(fig_cship, use_container_width=True)

# ── 4f · Category-level risk matrix ──────────────────────────────────────────
with r6:
    cat_risk = (
        df.groupby("Product_Category")
        .agg(
            Sales=("Total_Sales", "sum"),
            Profit=("Profit", "sum"),
            Shipping=("Shipping_Cost", "sum"),
            Orders=("Order_ID", "nunique"),
        )
        .reset_index()
    )
    cat_risk["Margin_%"]     = (cat_risk["Profit"] / cat_risk["Sales"] * 100).round(1)
    cat_risk["Ship_%_Sales"] = (cat_risk["Shipping"] / cat_risk["Sales"] * 100).round(2)

    fig_cat_risk = px.scatter(
        cat_risk,
        x="Sales", y="Margin_%",
        size="Shipping",
        color="Product_Category",
        text="Product_Category",
        title="Category Risk: Sales vs Margin (bubble = shipping cost)",
        color_discrete_sequence=PALETTE,
        labels={"Sales": "Total Sales ($)", "Margin_%": "Profit Margin %"},
    )
    fig_cat_risk.update_traces(textposition="top center")
    plotly_defaults(fig_cat_risk, height=340)
    st.plotly_chart(fig_cat_risk, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 5 · MANAGEMENT ACTIONS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">⑤ MANAGEMENT ACTIONS & DATA-DRIVEN INSIGHTS</div>', unsafe_allow_html=True)

# --- compute insight variables dynamically ---
# Best region
best_region = region_grp.loc[region_grp["Sales"].idxmax(), "Region"]
best_region_margin = region_grp.loc[region_grp["Sales"].idxmax(), "Margin_%"]

# Worst-margin category
worst_cat  = cat_grp.loc[cat_grp["Margin_%"].idxmin(), "Product_Category"]
worst_margin = cat_grp["Margin_%"].min()

# Best-margin category
best_cat  = cat_grp.loc[cat_grp["Margin_%"].idxmax(), "Product_Category"]
best_cat_margin = cat_grp["Margin_%"].max()

# Discount impact
no_disc_margin  = disc_grp[disc_grp["Discount_Band"] == "0%"]["Margin_%"].values
high_disc_margin = disc_grp[disc_grp["Discount_Band"] == "21-30%"]["Margin_%"].values
no_disc_m  = float(no_disc_margin[0])  if len(no_disc_margin)  else 0
hi_disc_m  = float(high_disc_margin[0]) if len(high_disc_margin) else 0

# High shipping country
hi_ship_country = high_ship.iloc[-1]["Country"]
hi_ship_pct     = high_ship.iloc[-1]["Ship_%_Sales"]

# Best segment
best_seg = seg_grp.loc[seg_grp["Sales"].idxmax(), "Customer_Segment"]
best_seg_aov = seg_grp.loc[seg_grp["Sales"].idxmax(), "AOV"]

# Low margin product count
low_m_count = int((prod_risk["Margin_%"] < 20).sum())

# Top product
top_prod = prod_grp.nlargest(1, "Sales").iloc[0]

insights = [
    (
        "opp",
        f"🌍 Regional Growth Opportunity — {best_region}",
        f"{best_region} leads in total sales with a profit margin of {best_region_margin:.1f}%. "
        f"Management should prioritise marketing investment and customer acquisition in this region to capitalise on existing momentum. "
        f"Consider replicating successful product mixes from {best_region} into lower-performing regions.",
    ),
    (
        "risk",
        f"⚠️ Discount Erosion Risk",
        f"Orders with no discount achieve a profit margin of {no_disc_m:.1f}%, "
        f"while orders discounted at 21–30% show a margin of {hi_disc_m:.1f}%. "
        f"Heavy discounting significantly compresses profitability. "
        f"Management should establish a discount approval policy, set a minimum margin floor, "
        f"and limit blanket promotions in favour of targeted, segment-specific offers.",
    ),
    (
        "risk",
        f"🚚 Shipping Cost Alert — {hi_ship_country}",
        f"{hi_ship_country} has the highest shipping cost as a percentage of sales ({hi_ship_pct:.1f}%). "
        f"This structural cost drag erodes margins. Management should renegotiate carrier contracts for high-cost countries, "
        f"consider consolidated shipment schedules, or introduce minimum-order thresholds to offset logistics costs.",
    ),
    (
        "risk" if worst_margin < 25 else "warn",
        f"📦 Low-Margin Category — {worst_cat}",
        f"{worst_cat} carries the lowest profit margin at {worst_margin:.1f}%. "
        f"A pricing review should be conducted. If cost reduction is not achievable, management may consider "
        f"repositioning or reducing SKU depth in this category, or bundling with higher-margin items.",
    ),
    (
        "opp",
        f"⭐ High-Margin Category to Scale — {best_cat}",
        f"{best_cat} delivers the strongest profit margin at {best_cat_margin:.1f}%. "
        f"Expanding the product range, increasing inventory depth, and prioritising this category in promotional campaigns "
        f"would yield the highest return on marketing spend.",
    ),
    (
        "opp",
        f"👥 Customer Segment Focus — {best_seg}",
        f"The {best_seg} segment generates the highest average order value of {fmt_currency(best_seg_aov)}. "
        f"Management should invest in retention programmes for this segment (e.g., account management, loyalty incentives) "
        f"and design targeted acquisition campaigns to grow this cohort.",
    ),
    (
        "warn",
        f"🔍 Product Portfolio Review — {low_m_count} Low-Margin Products",
        f"{low_m_count} products (out of {len(prod_risk)}) deliver a profit margin below 20% and have above-median sales. "
        f"These are classified as high-risk in the sales vs margin matrix. "
        f"A product-level cost audit, price review, or rationalisation of the long tail should be undertaken quarterly.",
    ),
    (
        "opp",
        f"🏆 Top Product — {top_prod['Product_Name']}",
        f"{top_prod['Product_Name']} is the best-selling product with ${top_prod['Sales']:,.0f} in total sales. "
        f"Ensuring consistent stock availability, strong placement in marketing materials, "
        f"and cross-sell pairings with complementary products will protect and grow this revenue stream.",
    ),
]

for kind, title, body in insights:
    st.markdown(
        f'<div class="insight-box {kind}"><strong>{title}</strong><br>{body}</div>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# DATA TABLE
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("📋 View Filtered Raw Data", expanded=False):
    display_cols = [
        "Order_ID", "Order_Date", "Customer_Segment", "Country", "Region",
        "Product_Category", "Product_Name", "Quantity", "Unit_Price",
        "Discount_Percent", "Total_Sales", "Shipping_Cost", "Profit",
        "Payment_Method",
    ]
    st.dataframe(
        df[display_cols].sort_values("Order_Date", ascending=False),
        use_container_width=True,
        height=350,
    )
    st.caption(f"Showing {len(df):,} rows matching current filters.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><span style='color:#94a3b8;font-size:0.78rem;'>"
    "E-Commerce BI Dashboard · Built with Streamlit, Plotly & Pandas · "
    "Dataset: Global E-Commerce Sales (Kaggle)"
    "</span></center>",
    unsafe_allow_html=True,
)

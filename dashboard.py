import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="EV Charging Network Intelligence",
    layout="wide",
    page_icon="⚡",
)

# -----------------------------
# HELPERS
# -----------------------------
def safe_col(df: pd.DataFrame, name: str) -> bool:
    return name in df.columns

def to_num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")

def pct(a: float, b: float) -> float:
    if b == 0 or pd.isna(b):
        return 0.0
    return float(a) / float(b) * 100.0

def top_n_with_other(df_counts: pd.DataFrame, label_col: str, value_col: str, n: int = 10):
    df_counts = df_counts.copy()
    df_counts = df_counts.sort_values(value_col, ascending=False)
    top = df_counts.head(n)
    other_val = df_counts.iloc[n:][value_col].sum() if len(df_counts) > n else 0
    if other_val > 0:
        other = pd.DataFrame({label_col: ["Other"], value_col: [other_val]})
        top = pd.concat([top, other], ignore_index=True)
    return top

def insight(text: str):
    st.markdown(
        f"""
        <div style="
            padding: 12px 14px;
            border-radius: 12px;
            border: 1px solid rgba(120,120,120,0.25);
            background: rgba(120,120,120,0.07);
            margin: 6px 0 12px 0;">
            <span style="font-weight:600;">Insight:</span> {text}
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# DATA LOAD (NREL AFDC API)
# -----------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def load_data_from_api() -> pd.DataFrame:
    api_key = st.secrets["NREL_API_KEY"]

    url = (
        "https://developer.nrel.gov/api/alt-fuel-stations/v1.csv?"
        f"api_key={api_key}"
        "&fuel_type=ELEC"
        "&limit=all"
    )

    df = pd.read_csv(url)
    df.columns = df.columns.str.lower().str.strip()
    return df

with st.spinner("Loading live federal infrastructure data…"):
    df = load_data_from_api()

if df.empty:
    st.error("No data returned from API.")
    st.stop()

# Normalize a few common columns
# Some endpoints vary; this keeps us resilient.
col_state = "state"
col_network = "ev network"
col_access = "access code"
col_status = "status code"
col_lat = "latitude"
col_lon = "longitude"
col_open = "open date"
col_last = "date last confirmed"

# Charger counts (present in many AFDC exports; not always in API CSV)
col_l2 = "ev level2 evse num"
col_dc = "ev dc fast count"  # sometimes "ev dc fast num" elsewhere

# Fallbacks if schema varies
if not safe_col(df, col_dc) and safe_col(df, "ev dc fast num"):
    col_dc = "ev dc fast num"

# Clean up key fields
if safe_col(df, col_network):
    df[col_network] = df[col_network].fillna("Unknown").astype(str)
else:
    df[col_network] = "Unknown"

if not safe_col(df, col_state):
    df[col_state] = "N/A"

if safe_col(df, col_access):
    df[col_access] = df[col_access].fillna("Unknown").astype(str)
else:
    df[col_access] = "Unknown"

if safe_col(df, col_status):
    df[col_status] = df[col_status].fillna("Unknown").astype(str)
else:
    df[col_status] = "Unknown"

for c in [col_l2, col_dc]:
    if safe_col(df, c):
        df[c] = to_num(df[c]).fillna(0)

for c in [col_lat, col_lon]:
    if safe_col(df, c):
        df[c] = to_num(df[c])

# -----------------------------
# SIDEBAR (Enterprise Filters)
# -----------------------------
st.sidebar.title("Controls")
st.sidebar.caption("Filter the competitive landscape")

all_states = sorted(df[col_state].dropna().astype(str).unique().tolist())
all_networks = sorted(df[col_network].dropna().astype(str).unique().tolist())
all_access = sorted(df[col_access].dropna().astype(str).unique().tolist())

default_states = all_states[:]  # all
default_networks = all_networks[:]  # all

selected_states = st.sidebar.multiselect("State(s)", all_states, default=default_states)
selected_networks = st.sidebar.multiselect("Network(s)", all_networks, default=default_networks)
selected_access = st.sidebar.multiselect("Access", all_access, default=all_access)

# Status filter if present
status_vals = sorted(df[col_status].dropna().astype(str).unique().tolist())
selected_status = st.sidebar.multiselect("Status", status_vals, default=status_vals)

# Map performance
max_map_points = st.sidebar.slider("Map points (performance)", 500, 8000, 4000, 500)

# Apply filters
f = df[
    df[col_state].astype(str).isin(selected_states)
    & df[col_network].astype(str).isin(selected_networks)
    & df[col_access].astype(str).isin(selected_access)
    & df[col_status].astype(str).isin(selected_status)
].copy()

if f.empty:
    st.warning("No rows match your filters. Widen filters in the sidebar.")
    st.stop()

# -----------------------------
# HEADER
# -----------------------------
st.title("EV Charging Network Competitive Intelligence")
st.caption("Live federal infrastructure data • NREL AFDC API • Market share, power strategy, and geographic dominance")

# -----------------------------
# KPI ROW (Executive Summary)
# -----------------------------
total_stations = len(f)
states_covered = f[col_state].nunique()
networks_covered = f[col_network].nunique()

active_like = None
if safe_col(f, col_status):
    # AFDC often uses E for "Existing"
    active_like = int((f[col_status].astype(str).str.upper() == "E").sum())

# Port totals if available
l2_total = int(f[col_l2].sum()) if safe_col(f, col_l2) else None
dc_total = int(f[col_dc].sum()) if safe_col(f, col_dc) else None

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Stations", f"{total_stations:,}")
k2.metric("States", f"{states_covered:,}")
k3.metric("Networks", f"{networks_covered:,}")
k4.metric("Existing (Status=E)", f"{active_like:,}" if active_like is not None else "N/A")
if l2_total is not None and dc_total is not None:
    k5.metric("DC Fast Share", f"{pct(dc_total, (dc_total + l2_total)):.1f}%")
else:
    k5.metric("DC Fast Share", "N/A")

# Insight callout (executive framing)
top_net = f[col_network].value_counts().index[0]
top_net_share = pct(f[col_network].value_counts().iloc[0], total_stations)
insight(f"Top network in the current view is **{top_net}** with **{top_net_share:.1f}%** of stations. Use filters to evaluate dominance, fragmentation, and whitespace.")

st.markdown("---")

# -----------------------------
# TABS (Enterprise IA)
# -----------------------------
tab_overview, tab_compete, tab_geo, tab_data = st.tabs(
    ["Executive Overview", "Competitive Landscape", "Geography", "Data Explorer"]
)

# =============================
# TAB: Executive Overview
# =============================
with tab_overview:
    left, right = st.columns([1.2, 1])

    # Top States by Stations
    if safe_col(f, col_state):
        state_counts = (
            f.groupby(col_state).size().reset_index(name="stations")
            .sort_values("stations", ascending=False)
        )
    else:
        state_counts = pd.DataFrame({"state": [], "stations": []})

    with left:
        st.subheader("Top States by Station Footprint")
        fig_states = px.bar(
            state_counts.head(15),
            x=col_state,
            y="stations",
            text="stations",
        )
        fig_states.update_traces(textposition="outside")
        fig_states.update_layout(height=420, xaxis_title="State", yaxis_title="Stations")
        st.plotly_chart(fig_states, use_container_width=True)

    with right:
        st.subheader("Access Model Mix")
        access_counts = (
            f[col_access].value_counts().reset_index()
        )
        access_counts.columns = ["access", "stations"]
        access_top = top_n_with_other(access_counts, "access", "stations", n=6)

        fig_access = px.pie(
            access_top,
            names="access",
            values="stations",
            hole=0.5,
        )
        fig_access.update_layout(height=420)
        st.plotly_chart(fig_access, use_container_width=True)

    # Charger mix (if available)
    st.subheader("Charging Power Mix")
    if safe_col(f, col_l2) and safe_col(f, col_dc):
        tech = pd.DataFrame({
            "type": ["Level 2 ports", "DC Fast ports"],
            "ports": [int(f[col_l2].sum()), int(f[col_dc].sum())],
        })
        fig_ports = px.bar(tech, x="type", y="ports", text="ports")
        fig_ports.update_traces(textposition="outside")
        fig_ports.update_layout(height=380, xaxis_title="", yaxis_title="Ports")
        st.plotly_chart(fig_ports, use_container_width=True)

        dc_share = pct(tech.loc[1, "ports"], tech["ports"].sum())
        insight(f"Within the filtered market, **DC Fast represents {dc_share:.1f}%** of ports—use this to compare network strategy (corridor-focused vs destination/workplace).")
    else:
        st.info("Port-level fields (Level 2 / DC Fast) are not present in this API response view. Market share and dominance still work at the station level.")

# =============================
# TAB: Competitive Landscape
# =============================
with tab_compete:
    st.subheader("Market Share by Network")

    net_counts = f[col_network].value_counts().reset_index()
    net_counts.columns = ["network", "stations"]
    net_counts["market_share_pct"] = (net_counts["stations"] / net_counts["stations"].sum() * 100).round(2)

    c1, c2 = st.columns([1.3, 1])

    with c1:
        fig_share = px.bar(
            net_counts.head(12),
            x="network",
            y="market_share_pct",
            text="market_share_pct",
        )
        fig_share.update_traces(textposition="outside")
        fig_share.update_layout(height=450, xaxis_title="Network", yaxis_title="Market Share (%)")
        st.plotly_chart(fig_share, use_container_width=True)

    with c2:
        st.markdown("#### Concentration")
        # Simple HHI (Herfindahl-Hirschman Index) based on station share
        shares = (net_counts["stations"] / net_counts["stations"].sum()).values
        hhi = float(np.sum((shares * 100) ** 2))  # scaled 0-10,000
        st.metric("HHI (stations)", f"{hhi:,.0f}")
        if hhi < 1500:
            insight("Market is **unconcentrated** (fragmented). Expansion can focus on stitching whitespace.")
        elif hhi < 2500:
            insight("Market is **moderately concentrated**. Expect competitive responses in leader states.")
        else:
            insight("Market is **highly concentrated**. Leaders dominate—target underserved micro-regions or differentiate on power mix.")

    st.markdown("---")

    st.subheader("DC Fast Strategy by Network (if available)")
    if safe_col(f, col_l2) and safe_col(f, col_dc):
        mix = (
            f.groupby(col_network)
            .agg(l2_ports=(col_l2, "sum"), dc_ports=(col_dc, "sum"))
            .fillna(0)
            .reset_index()
        )
        mix["total_ports"] = mix["l2_ports"] + mix["dc_ports"]
        mix["dc_fast_pct"] = np.where(mix["total_ports"] > 0, (mix["dc_ports"] / mix["total_ports"]) * 100, 0)
        mix = mix.sort_values("dc_fast_pct", ascending=False)

        fig_dc = px.bar(
            mix.head(12),
            x=col_network,
            y="dc_fast_pct",
            text="dc_fast_pct",
        )
        fig_dc.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_dc.update_layout(height=450, xaxis_title="Network", yaxis_title="DC Fast Share of Ports (%)")
        st.plotly_chart(fig_dc, use_container_width=True)

        # Competitive narrative
        top_strategy = mix.head(1).iloc[0]
        insight(
            f"**{top_strategy[col_network]}** is the most DC-Fast-weighted in the current view "
            f"(**{top_strategy['dc_fast_pct']:.1f}%** of ports). That indicates corridor/turnover positioning vs destination charging."
        )
    else:
        st.info("DC Fast / Level 2 fields not present here—keep using station market share + geography, or switch to a richer endpoint later.")

    st.markdown("---")

    st.subheader("State Dominance (Leader by State)")
    leader = (
        f.groupby([col_state, col_network]).size().reset_index(name="stations")
    )
    leader = leader.loc[leader.groupby(col_state)["stations"].idxmax()].sort_values("stations", ascending=False)

    fig_leader = px.bar(
        leader.head(20),
        x=col_state,
        y="stations",
        color=col_network,
        text="stations",
    )
    fig_leader.update_traces(textposition="outside")
    fig_leader.update_layout(height=520, xaxis_title="State", yaxis_title="Leader Stations")
    st.plotly_chart(fig_leader, use_container_width=True)

    insight("Use this to spot **defensible strongholds** (network dominates state) vs **contested markets** (low leader station count).")

# =============================
# TAB: Geography
# =============================
with tab_geo:
    st.subheader("Network Footprint Map (sampled for performance)")

    if safe_col(f, col_lat) and safe_col(f, col_lon):
        geo = f.dropna(subset=[col_lat, col_lon]).copy()
        if len(geo) > max_map_points:
            geo = geo.sample(max_map_points, random_state=42)

        fig_map = px.scatter_mapbox(
            geo,
            lat=col_lat,
            lon=col_lon,
            color=col_network,
            hover_name="station name" if safe_col(geo, "station name") else None,
            hover_data={
                col_state: True,
                col_access: True,
            },
            zoom=3,
            height=650,
        )
        fig_map.update_layout(mapbox_style="carto-positron")
        st.plotly_chart(fig_map, use_container_width=True)

        insight("Map is sampled for speed. Use filters to focus on a state or network, then increase map points if needed.")
    else:
        st.info("Latitude/Longitude not available in the current response.")

    st.markdown("---")

    st.subheader("Whitespace Finder (simple)")
    st.caption("Quick heuristic: states where a network has low presence relative to total stations in that state.")

    # Whitespace: for a chosen network, compare its share by state
    focus_network = st.selectbox("Choose a network to assess whitespace", all_networks, index=0 if all_networks else 0)

    by_state_total = f.groupby(col_state).size().reset_index(name="state_total_stations")
    by_state_net = f[f[col_network] == focus_network].groupby(col_state).size().reset_index(name="network_stations")
    ws = by_state_total.merge(by_state_net, on=col_state, how="left").fillna({"network_stations": 0})
    ws["network_share_pct_in_state"] = (ws["network_stations"] / ws["state_total_stations"] * 100).round(2)

    # show lowest share states but with meaningful total stations
    ws = ws.sort_values(["network_share_pct_in_state", "state_total_stations"], ascending=[True, False])

    fig_ws = px.bar(
        ws.head(15),
        x=col_state,
        y="network_share_pct_in_state",
        text="network_share_pct_in_state",
    )
    fig_ws.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig_ws.update_layout(height=450, xaxis_title="State", yaxis_title=f"{focus_network} share of stations in state (%)")
    st.plotly_chart(fig_ws, use_container_width=True)

    insight(f"Lowest-share states for **{focus_network}** are candidate whitespace markets—validate against DC Fast strategy and access model for fit.")

# =============================
# TAB: Data Explorer
# =============================
with tab_data:
    st.subheader("Filtered Dataset")
    st.caption("Use this to inspect the schema and spot additional fields you want to add to competitive views.")
    show_cols = st.multiselect(
        "Columns to display",
        options=f.columns.tolist(),
        default=[c for c in [col_network, col_state, col_access, col_status, col_lat, col_lon] if c in f.columns],
    )
    st.dataframe(f[show_cols].head(500) if show_cols else f.head(500), use_container_width=True)

    st.markdown("---")
    st.subheader("Schema / Columns")
    st.code(", ".join(f.columns.tolist()), language="text")

# Footer
st.caption(f"Last refreshed: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} • Cached for 1 hour")

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="EV Charging Market Structure Intelligence",
    layout="wide"
)

st.title("EV Charging Market Structure & Competitive Intelligence")
st.markdown("Live federal infrastructure data via NREL AFDC API")

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data(ttl=3600)
def load_data():
    API_KEY = st.secrets["NREL_API_KEY"]

    DATA_URL = (
        "https://developer.nrel.gov/api/alt-fuel-stations/v1.csv?"
        f"api_key={API_KEY}"
        "&fuel_type=ELEC"
        "&limit=all"
    )

    df = pd.read_csv(DATA_URL)
    df.columns = df.columns.str.lower()
    return df

df = load_data()

if df.empty:
    st.error("No data returned from API.")
    st.stop()

# -------------------------------------------------
# NATIONAL STRUCTURE METRICS
# -------------------------------------------------
st.header("Market Structure Overview")

total_stations = len(df)

network_counts = (
    df["ev network"]
    .fillna("Unknown")
    .value_counts()
    .reset_index()
)

network_counts.columns = ["Network", "Stations"]

network_counts["Market Share"] = (
    network_counts["Stations"] / network_counts["Stations"].sum()
)

# Herfindahl-Hirschman Index (HHI)
hhi = (network_counts["Market Share"] ** 2).sum()

top5_share = network_counts.head(5)["Market Share"].sum()

fragmentation = 1 - top5_share

col1, col2, col3 = st.columns(3)
col1.metric("Total Stations", f"{total_stations:,}")
col2.metric("Top 5 Market Share", f"{top5_share*100:.1f}%")
col3.metric("HHI (Concentration Index)", f"{hhi:.3f}")

st.divider()

# -------------------------------------------------
# MARKET SHARE CHART
# -------------------------------------------------
st.header("Network Market Share")

fig_market = px.bar(
    network_counts.head(10),
    x="Network",
    y=network_counts.head(10)["Market Share"] * 100,
    text=(network_counts.head(10)["Market Share"] * 100).round(2),
    labels={"y": "Market Share (%)"},
    color=network_counts.head(10)["Market Share"] * 100,
    color_continuous_scale="Blues"
)

st.plotly_chart(fig_market, use_container_width=True)

st.divider()

# -------------------------------------------------
# POWER STRATEGY POSITIONING
# -------------------------------------------------
st.header("Power Strategy Positioning (DC Fast Focus)")

if "ev dc fast count" in df.columns and "ev level2 evse num" in df.columns:

    network_mix = (
        df.groupby("ev network")
        .agg({
            "ev dc fast count": "sum",
            "ev level2 evse num": "sum"
        })
        .fillna(0)
        .reset_index()
    )

    network_mix["Total Ports"] = (
        network_mix["ev dc fast count"] +
        network_mix["ev level2 evse num"]
    )

    network_mix["DC Fast %"] = (
        network_mix["ev dc fast count"] /
        network_mix["Total Ports"]
    ).fillna(0) * 100

    fig_power = px.scatter(
        network_mix,
        x="Total Ports",
        y="DC Fast %",
        text="ev network",
        size="Total Ports",
        color="DC Fast %",
        color_continuous_scale="Reds"
    )

    fig_power.update_traces(textposition="top center")

    st.plotly_chart(fig_power, use_container_width=True)

st.divider()

# -------------------------------------------------
# STATE DOMINANCE ANALYSIS
# -------------------------------------------------
st.header("State-Level Market Leaders")

state_network = (
    df.groupby(["state", "ev network"])
    .size()
    .reset_index(name="Stations")
)

leaders = state_network.loc[
    state_network.groupby("state")["Stations"].idxmax()
]

fig_leaders = px.bar(
    leaders.sort_values("Stations", ascending=False).head(15),
    x="state",
    y="Stations",
    text="Stations",
    color="ev network"
)

st.plotly_chart(fig_leaders, use_container_width=True)

st.divider()

# -------------------------------------------------
# EXPANSION OPPORTUNITY SIGNAL
# -------------------------------------------------
st.header("Expansion Opportunity Signal")

state_totals = (
    df.groupby("state")
    .size()
    .reset_index(name="Stations")
)

median_density = state_totals["Stations"].median()

state_totals["Below Median Density"] = state_totals["Stations"] < median_density

fig_opportunity = px.bar(
    state_totals.sort_values("Stations").head(15),
    x="state",
    y="Stations",
    color="Below Median Density"
)

st.plotly_chart(fig_opportunity, use_container_width=True)

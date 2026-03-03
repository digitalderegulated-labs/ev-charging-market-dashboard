import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="EV Charging Network Competitive Intelligence",
    layout="wide"
)

st.title("EV Charging Network Competitive Intelligence Platform")
st.markdown("Live federal infrastructure data via NREL AFDC API")

# -------------------------------------------------
# LOAD DATA FROM NREL API
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
# NATIONAL OVERVIEW
# -------------------------------------------------
st.header("National Infrastructure Overview")

total_stations = len(df)
states_covered = df["state"].nunique() if "state" in df.columns else 0
networks = df["ev network"].nunique() if "ev network" in df.columns else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Stations", f"{total_stations:,}")
col2.metric("States Covered", states_covered)
col3.metric("Active Networks", networks)

st.divider()

# -------------------------------------------------
# NETWORK MARKET SHARE
# -------------------------------------------------
st.header("Network Market Share")

if "ev network" in df.columns:

    network_counts = (
        df["ev network"]
        .fillna("Unknown")
        .value_counts()
        .reset_index()
    )

    network_counts.columns = ["Network", "Stations"]

    network_counts["Market Share %"] = (
        network_counts["Stations"] /
        network_counts["Stations"].sum() * 100
    ).round(2)

    fig_market = px.bar(
        network_counts.head(10),
        x="Network",
        y="Market Share %",
        text="Market Share %",
        color="Market Share %",
        color_continuous_scale="Blues"
    )

    st.plotly_chart(fig_market, use_container_width=True)

st.divider()

# -------------------------------------------------
# DC FAST STRATEGY BY NETWORK
# -------------------------------------------------
st.header("Charging Power Strategy (DC Fast %)")

if "ev network" in df.columns and \
   "ev dc fast count" in df.columns and \
   "ev level2 evse num" in df.columns:

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

    fig_mix = px.bar(
        network_mix.sort_values("DC Fast %", ascending=False).head(10),
        x="ev network",
        y="DC Fast %",
        text="DC Fast %",
        color="DC Fast %",
        color_continuous_scale="Reds"
    )

    st.plotly_chart(fig_mix, use_container_width=True)

st.divider()

# -------------------------------------------------
# TOP STATES
# -------------------------------------------------
st.header("Top 15 States by Infrastructure Density")

if "state" in df.columns:

    state_counts = (
        df.groupby("state")
        .size()
        .reset_index(name="Stations")
        .sort_values("Stations", ascending=False)
    )

    fig_states = px.bar(
        state_counts.head(15),
        x="state",
        y="Stations",
        text="Stations",
        color="Stations",
        color_continuous_scale="Greens"
    )

    st.plotly_chart(fig_states, use_container_width=True)

st.divider()

# -------------------------------------------------
# STATE MARKET LEADER
# -------------------------------------------------
st.header("Market Leader by State")

if "state" in df.columns and "ev network" in df.columns:

    state_network = (
        df.groupby(["state", "ev network"])
        .size()
        .reset_index(name="Stations")
    )

    leaders = state_network.loc[
        state_network.groupby("state")["Stations"].idxmax()
    ]

    fig_leader = px.bar(
        leaders.sort_values("Stations", ascending=False).head(15),
        x="state",
        y="Stations",
        text="Stations",
        color="ev network"
    )

    st.plotly_chart(fig_leader, use_container_width=True)

st.divider()

# -------------------------------------------------
# MAP
# -------------------------------------------------
st.header("Geographic Distribution")

if "latitude" in df.columns and "longitude" in df.columns:

    fig_map = px.scatter_mapbox(
        df.sample(min(len(df), 5000)),  # performance safety
        lat="latitude",
        lon="longitude",
        color="ev network" if "ev network" in df.columns else None,
        zoom=3,
        height=600
    )

    fig_map.update_layout(mapbox_style="carto-positron")

    st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# -------------------------------------------------
# STATE DRILLDOWN
# -------------------------------------------------
st.header("State Drilldown")

if "state" in df.columns:

    selected_state = st.selectbox(
        "Select State",
        sorted(df["state"].dropna().unique())
    )

    state_df = df[df["state"] == selected_state]

    st.metric(
        f"Stations in {selected_state}",
        f"{len(state_df):,}"
    )

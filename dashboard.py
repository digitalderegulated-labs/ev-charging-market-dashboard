import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="EV Charging Network Intelligence",
    layout="wide"
)

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
# SIDEBAR FILTERS (Enterprise Feel)
# -------------------------------------------------
st.sidebar.title("Filters")

states = sorted(df["state"].dropna().unique())
networks = sorted(df["ev network"].dropna().unique())

selected_states = st.sidebar.multiselect(
    "Select State(s)",
    states,
    default=states
)

selected_networks = st.sidebar.multiselect(
    "Select Network(s)",
    networks,
    default=networks
)

filtered_df = df[
    (df["state"].isin(selected_states)) &
    (df["ev network"].isin(selected_networks))
]

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("EV Charging Network Competitive Intelligence")
st.caption("Live Federal Infrastructure Data • NREL AFDC API")

# -------------------------------------------------
# KPI ROW
# -------------------------------------------------
total_stations = len(filtered_df)
states_covered = filtered_df["state"].nunique()
networks_count = filtered_df["ev network"].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("Stations", f"{total_stations:,}")
col2.metric("States", states_covered)
col3.metric("Networks", networks_count)

st.markdown("---")

# -------------------------------------------------
# MARKET SHARE
# -------------------------------------------------
st.subheader("Network Market Share")

network_counts = (
    filtered_df["ev network"]
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

fig_market.update_layout(height=450)
st.plotly_chart(fig_market, use_container_width=True)

st.markdown("---")

# -------------------------------------------------
# DC FAST STRATEGY
# -------------------------------------------------
st.subheader("Charging Power Strategy (DC Fast %)")

network_mix = (
    filtered_df.groupby("ev network")
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

fig_mix.update_layout(height=450)
st.plotly_chart(fig_mix, use_container_width=True)

st.markdown("---")

# -------------------------------------------------
# STATE DENSITY
# -------------------------------------------------
st.subheader("State Infrastructure Density")

state_counts = (
    filtered_df.groupby("state")
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

fig_states.update_layout(height=450)
st.plotly_chart(fig_states, use_container_width=True)

st.markdown("---")

# -------------------------------------------------
# MAP
# -------------------------------------------------
st.subheader("Geographic Distribution")

fig_map = px.scatter_mapbox(
    filtered_df.sample(min(len(filtered_df), 5000)),
    lat="latitude",
    lon="longitude",
    color="ev network",
    zoom=3,
    height=600
)

fig_map.update_layout(mapbox_style="carto-positron")

st.plotly_chart(fig_map, use_container_width=True)

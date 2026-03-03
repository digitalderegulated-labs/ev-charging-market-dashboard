import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="EV Market Intelligence Dashboard",
    layout="wide"
)

st.title("EV Charging Market Intelligence Dashboard")
st.markdown("Live data from U.S. Department of Energy AFDC.")

# -----------------------------
# API CONFIG
# -----------------------------
API_KEY = st.secrets["NREL_API_KEY"]

DATA_URL = (
    "https://developer.nrel.gov/api/alt-fuel-stations/v1.csv?"
    f"api_key={API_KEY}"
    "&fuel_type=ELEC"
    "&limit=all"
)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    df.columns = df.columns.str.lower()
    return df

try:
    df = load_data()
except Exception as e:
    st.error("Error loading data from NREL API.")
    st.stop()

if df.empty:
    st.error("No data returned from API.")
    st.stop()

# -----------------------------
# HIGH LEVEL METRICS
# -----------------------------
total_stations = len(df)
total_states = df["state"].nunique()
if "ev_network" in df.columns:
    unique_networks = df["ev_network"].nunique()
else:
    unique_networks = "N/A"

col1, col2, col3 = st.columns(3)
col1.metric("Total EV Charging Stations (US)", f"{total_stations:,}")
col2.metric("States Represented", total_states)
col3.metric("Charging Networks", unique_networks)

st.divider()

# -----------------------------
# TOP STATES BAR CHART
# -----------------------------
state_counts = (
    df.groupby("state")
      .size()
      .reset_index(name="stations")
      .sort_values("stations", ascending=False)
)

st.subheader("Top 15 States by EV Charging Infrastructure")

fig_states = px.bar(
    state_counts.head(15),
    x="state",
    y="stations",
    text="stations",
    color="stations",
    color_continuous_scale="Blues"
)

fig_states.update_traces(textposition="outside")
fig_states.update_layout(
    xaxis_title="State",
    yaxis_title="Total Stations",
    height=500
)

st.plotly_chart(fig_states, use_container_width=True)

st.divider()

# -----------------------------
# STATE EXPLORER
# -----------------------------
st.subheader("Explore Individual State")

selected_state = st.selectbox(
    "Choose a state",
    sorted(df["state"].unique())
)

state_df = df[df["state"] == selected_state]

st.metric(
    f"Total Stations in {selected_state}",
    f"{len(state_df):,}"
)

# -----------------------------
# EV CHARGER TYPE BREAKDOWN
# -----------------------------
st.subheader("Charger Type Breakdown")

level2 = 0
dc_fast = 0

if "ev_level2_evse_num" in state_df.columns:
    level2 = state_df["ev_level2_evse_num"].fillna(0).sum()

if "ev_dc_fast_num" in state_df.columns:
    dc_fast = state_df["ev_dc_fast_num"].fillna(0).sum()

charger_data = pd.DataFrame({
    "Charger Type": ["Level 2", "DC Fast"],
    "Total Units": [level2, dc_fast]
})

fig_types = px.bar(
    charger_data,
    x="Charger Type",
    y="Total Units",
    text="Total Units",
    color="Charger Type"
)

fig_types.update_layout(height=400)

st.plotly_chart(fig_types, use_container_width=True)

st.divider()

# -----------------------------
# NETWORK RANKING
# -----------------------------
st.subheader("Top Charging Networks (Selected State)")

network_counts = (
    state_df.groupby("ev_network")
            .size()
            .reset_index(name="stations")
            .sort_values("stations", ascending=False)
)

fig_network = px.bar(
    network_counts.head(10),
    x="ev_network",
    y="stations",
    text="stations",
    color="stations",
    color_continuous_scale="Teal"
)

fig_network.update_layout(height=450)

st.plotly_chart(fig_network, use_container_width=True)

# redeploy trigger



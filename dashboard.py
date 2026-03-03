import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="US EV Charging Infrastructure Intelligence",
    layout="wide"
)

st.title("US EV Charging Infrastructure Intelligence Platform")
st.markdown("Live data from U.S. Department of Energy AFDC")

# ---------------------------------------------------
# LOAD DATA FROM NREL API
# ---------------------------------------------------
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

# ---------------------------------------------------
# NATIONAL OVERVIEW
# ---------------------------------------------------
st.header("National Infrastructure Overview")

total_stations = len(df)
states_covered = df["state"].nunique() if "state" in df.columns else 0
active = len(df[df["status code"] == "E"]) if "status code" in df.columns else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Stations", f"{total_stations:,}")
col2.metric("States Covered", states_covered)
col3.metric("Active Stations", f"{active:,}")

st.divider()

# ---------------------------------------------------
# ACCESS BREAKDOWN
# ---------------------------------------------------
st.header("Access Model")

if "access code" in df.columns:
    access_counts = df["access code"].fillna("Unknown").value_counts().reset_index()
    access_counts.columns = ["Access Type", "Stations"]

    fig_access = px.pie(
        access_counts,
        names="Access Type",
        values="Stations",
        hole=0.4
    )

    st.plotly_chart(fig_access, use_container_width=True)
else:
    st.info("Access data not available.")

st.divider()

# ---------------------------------------------------
# CHARGER TECHNOLOGY MIX
# ---------------------------------------------------
st.header("Charging Technology Mix")

level2_total = df["ev level2 evse num"].fillna(0).sum() if "ev level2 evse num" in df.columns else 0
dc_fast_total = df["ev dc fast count"].fillna(0).sum() if "ev dc fast count" in df.columns else 0

tech_df = pd.DataFrame({
    "Charger Type": ["Level 2", "DC Fast"],
    "Total Units": [level2_total, dc_fast_total]
})

fig_tech = px.bar(
    tech_df,
    x="Charger Type",
    y="Total Units",
    text="Total Units",
    color="Charger Type"
)

st.plotly_chart(fig_tech, use_container_width=True)

st.divider()

# ---------------------------------------------------
# TOP STATES
# ---------------------------------------------------
st.header("Top 15 States by Infrastructure")

if "state" in df.columns:
    state_counts = df.groupby("state").size().reset_index(name="Stations")
    state_counts = state_counts.sort_values("Stations", ascending=False)

    fig_states = px.bar(
        state_counts.head(15),
        x="state",
        y="Stations",
        text="Stations",
        color="Stations",
        color_continuous_scale="Blues"
    )

    st.plotly_chart(fig_states, use_container_width=True)

st.divider()

# ---------------------------------------------------
# NETWORK COMPETITION
# ---------------------------------------------------
st.header("Network Landscape")

if "ev network" in df.columns:
    network_counts = (
        df["ev network"]
        .fillna("Unknown")
        .value_counts()
        .reset_index()
    )
    network_counts.columns = ["Network", "Stations"]

    fig_network = px.bar(
        network_counts.head(10),
        x="Network",
        y="Stations",
        text="Stations",
        color="Stations",
        color_continuous_scale="Greens"
    )

    st.plotly_chart(fig_network, use_container_width=True)

st.divider()

# ---------------------------------------------------
# MAP
# ---------------------------------------------------
st.header("Geographic Distribution")

if "latitude" in df.columns and "longitude" in df.columns:
    fig_map = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        color="state",
        zoom=3,
        height=600
    )

    fig_map.update_layout(mapbox_style="carto-positron")

    st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# ---------------------------------------------------
# STATE DRILLDOWN
# ---------------------------------------------------
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

    if "ev level2 evse num" in state_df.columns and "ev dc fast count" in state_df.columns:
        state_level2 = state_df["ev level2 evse num"].fillna(0).sum()
        state_dc = state_df["ev dc fast count"].fillna(0).sum()

        state_mix = pd.DataFrame({
            "Type": ["Level 2", "DC Fast"],
            "Total Units": [state_level2, state_dc]
        })

        fig_state = px.bar(
            state_mix,
            x="Type",
            y="Total Units",
            text="Total Units",
            color="Type"
        )

        st.plotly_chart(fig_state, use_container_width=True)

import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

# -----------------------------
# PAGE CONFIG (Public-friendly)
# -----------------------------
st.set_page_config(
    page_title="US EV Charging Infrastructure Dashboard",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ US EV Charging Infrastructure Dashboard")
st.caption(
    "Live data from the U.S. Department of Energy AFDC (NREL). "
    "Built for public clarity + portfolio credibility."
)

# -----------------------------
# API + DATA LOADING
# -----------------------------
API_KEY = st.secrets["NREL_API_KEY"]

DATA_URL = (
    "https://developer.nrel.gov/api/alt-fuel-stations/v1.csv?"
    f"api_key={API_KEY}"
    "&fuel_type=ELEC"
    "&limit=all"
)

@st.cache_data(ttl=3600)
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

df = load_data(DATA_URL)

def ensure_col(name: str, default=None):
    if name not in df.columns:
        df[name] = default

# Ensure columns exist (avoid crashes)
ensure_col("state", "")
ensure_col("city", "")
ensure_col("station_name", "")
ensure_col("owner_type_code", "")
ensure_col("access_code", "")
ensure_col("groups_with_access_code", "")
ensure_col("ev_network", "Unknown")
ensure_col("ev_level1_evse_num", 0)
ensure_col("ev_level2_evse_num", 0)
ensure_col("ev_dc_fast_count", 0)
ensure_col("latitude", None)
ensure_col("longitude", None)

# Numeric conversions
for col in ["ev_level1_evse_num", "ev_level2_evse_num", "ev_dc_fast_count"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

df["state"] = df["state"].astype(str).str.strip().str.upper()
df["ev_network"] = df["ev_network"].fillna("Unknown").astype(str).replace({"": "Unknown"})

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filters")

all_states = sorted([s for s in df["state"].dropna().unique() if s and s != "NAN"])

selected_states = st.sidebar.multiselect(
    "Choose states (optional)",
    options=all_states,
    default=[],
    help="Leave empty to show the entire U.S.",
)

access_filter = st.sidebar.selectbox(
    "Access type",
    options=["All", "Public", "Private"],
    index=0,
    help="Public vs private station access (based on AFDC fields).",
)

network_filter = st.sidebar.selectbox(
    "Network (optional)",
    options=["All"] + sorted(df["ev_network"].unique().tolist()),
    index=0,
    help="Filter to a specific charging network if you want.",
)

show_map = st.sidebar.checkbox("Show map", value=True)
top_n_states = st.sidebar.slider("Top states to display", 10, 25, 15)

# Apply filters
filtered = df.copy()

if selected_states:
    filtered = filtered[filtered["state"].isin(selected_states)]

access_code = filtered["access_code"].astype(str).str.lower()
groups_access = filtered["groups_with_access_code"].astype(str).str.lower()

is_public = access_code.str.contains("public", na=False) | groups_access.str.contains("public", na=False)
is_private = access_code.str.contains("private", na=False) | groups_access.str.contains("private", na=False)

if access_filter == "Public":
    filtered = filtered[is_public]
elif access_filter == "Private":
    filtered = filtered[is_private]

if network_filter != "All":
    filtered = filtered[filtered["ev_network"].astype(str) == network_filter]

# -----------------------------
# KPI ROW
# -----------------------------
total_stations = len(filtered)
states_covered = filtered["state"].nunique()

level2_ports = int(filtered["ev_level2_evse_num"].sum())
dc_fast_ports = int(filtered["ev_dc_fast_count"].sum())
total_ports = max(level2_ports + dc_fast_ports, 1)
dc_share = round((dc_fast_ports / total_ports) * 100, 1)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Stations", f"{total_stations:,}")
c2.metric("States covered", f"{states_covered}")
c3.metric("Everyday chargers (Level 2 ports)", f"{level2_ports:,}")
c4.metric("Road-trip fast chargers (DC Fast ports)", f"{dc_fast_ports:,}")

st.divider()

# -----------------------------
# SECTION 1: Power mix
# -----------------------------
st.subheader("⚡ How fast is the charging network?")
st.write(
    "**Everyday chargers** (Level 2) are best for longer stops. "
    "**Fast chargers** (DC Fast) support quicker top-ups—more road-trip friendly."
)

mix_df = pd.DataFrame(
    {
        "Charger speed": ["Everyday chargers (Level 2)", "Road-trip fast chargers (DC Fast)"],
        "Ports": [level2_ports, dc_fast_ports],
    }
)

fig_mix = px.bar(mix_df, x="Charger speed", y="Ports", text="Ports")
fig_mix.update_layout(height=420, yaxis_title="Ports", xaxis_title="")
st.plotly_chart(fig_mix, use_container_width=True)

st.info(
    f"**Insight:** In this view, about **{dc_share}%** of ports are fast chargers. "
    "Higher fast-charger share typically signals stronger road-trip / corridor coverage."
)

st.divider()

# -----------------------------
# SECTION 2: Top states
# -----------------------------
st.subheader("🏁 Where is infrastructure most concentrated?")
state_counts = (
    filtered.groupby("state")
    .size()
    .reset_index(name="Stations")
    .sort_values("Stations", ascending=False)
)

fig_states = px.bar(
    state_counts.head(top_n_states),
    x="state",
    y="Stations",
    text="Stations",
    title=f"Top {top_n_states} states by station count",
)
fig_states.update_layout(height=450, xaxis_title="State", yaxis_title="Stations")
st.plotly_chart(fig_states, use_container_width=True)

st.divider()

# -----------------------------
# SECTION 3: State drilldown
# -----------------------------
st.subheader("🔎 Explore one state")

if filtered["state"].nunique() == 0:
    st.warning("No data matches your filters. Try clearing filters in the sidebar.")
else:
    state_choice = st.selectbox("Choose a state", options=sorted(filtered["state"].unique().tolist()))
    state_df = filtered[filtered["state"] == state_choice]

    st.metric(f"Stations in {state_choice}", f"{len(state_df):,}")

    lvl2 = int(state_df["ev_level2_evse_num"].sum())
    dcfc = int(state_df["ev_dc_fast_count"].sum())
    ports_total = max(lvl2 + dcfc, 1)
    state_dc_share = round((dcfc / ports_total) * 100, 1)

    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Everyday chargers (Level 2 ports)", f"{lvl2:,}")
    sc2.metric("Fast chargers (DC Fast ports)", f"{dcfc:,}")
    sc3.metric("Fast-charger share", f"{state_dc_share}%")

    st.subheader("🏢 Network landscape (top providers in this state)")
    network_counts = (
        state_df["ev_network"]
        .fillna("Unknown")
        .astype(str)
        .replace({"": "Unknown"})
        .value_counts()
        .head(10)
        .reset_index()
    )
    network_counts.columns = ["Network", "Stations"]

    fig_net = px.bar(network_counts, x="Network", y="Stations", text="Stations")
    fig_net.update_layout(height=420, xaxis_title="", yaxis_title="Stations")
    st.plotly_chart(fig_net, use_container_width=True)

    # -----------------------------
    # MAP (PyDeck - smoother + more interactive)
    # -----------------------------
    if show_map:
        st.subheader("🗺️ Map of station locations (interactive)")

        map_df = state_df.copy()

        map_df["latitude"] = pd.to_numeric(map_df["latitude"], errors="coerce")
        map_df["longitude"] = pd.to_numeric(map_df["longitude"], errors="coerce")
        map_df = map_df.dropna(subset=["latitude", "longitude"])

        if map_df.empty:
            st.warning("No valid coordinates available for this selection.")
        else:
            map_df = map_df[
                map_df["latitude"].between(10, 72) &
                map_df["longitude"].between(-170, -50)
            ]

            contiguous_only = st.checkbox("Show contiguous U.S. only (recommended)", value=True)
            if contiguous_only:
                map_df = map_df[
                    map_df["latitude"].between(24, 50) &
                    map_df["longitude"].between(-125, -66)
                ]

            if map_df.empty:
                st.warning("After cleaning coordinates, no points remain. Try widening filters.")
            else:
                map_df = map_df.sample(min(len(map_df), 8000), random_state=42)

                center_lat = float(map_df["latitude"].median())
                center_lon = float(map_df["longitude"].median())

                layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=map_df,
                    get_position="[longitude, latitude]",
                    get_radius=180,
                    pickable=True,
                    auto_highlight=True,
                    get_fill_color=[78, 121, 167, 140],
                )

                tooltip = {
                    "html": """
                        <b>{station_name}</b><br/>
                        {city}, {state}<br/>
                        Network: {ev_network}
                    """,
                    "style": {"backgroundColor": "rgba(10,10,10,0.85)", "color": "white"},
                }

                view_state = pdk.ViewState(
                    latitude=center_lat,
                    longitude=center_lon,
                    zoom=6,
                    pitch=0,
                )

                deck = pdk.Deck(
                    layers=[layer],
                    initial_view_state=view_state,
                    tooltip=tooltip,
                    map_style="mapbox://styles/mapbox/light-v10",
                )

                st.pydeck_chart(deck, use_container_width=True)

st.divider()

# -----------------------------
# SECTION 4: Download
# -----------------------------
st.subheader("📥 Download (for transparency)")
st.write("Want to explore the raw data behind the charts? Download the filtered dataset below.")

st.download_button(
    "Download filtered data as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="ev_charging_filtered.csv",
    mime="text/csv",
)

st.markdown("---")
st.caption("Built by Digital Deregulated Labs • Live federal infrastructure data via AFDC (NREL) API")


import streamlit as st
import pandas as pd
import plotly.express as px

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
    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

df = load_data(DATA_URL)

# Helper: safely get a column if it exists, else create it
def ensure_col(name: str, default=None):
    if name not in df.columns:
        df[name] = default

# Columns we may use (create if missing so app never crashes)
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
ensure_col("ev_connector_types", "")
ensure_col("ev_pricing", "")

# Make numeric columns numeric (important for charts)
for col in ["ev_level1_evse_num", "ev_level2_evse_num", "ev_dc_fast_count"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

# Clean up state values
df["state"] = df["state"].astype(str).str.strip().str.upper()

# -----------------------------
# SIDEBAR FILTERS (Public-friendly)
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
    options=["All"] + sorted(df["ev_network"].fillna("Unknown").astype(str).unique().tolist()),
    index=0,
    help="Filter to a specific charging network if you want.",
)

show_map = st.sidebar.checkbox("Show map", value=True)
top_n_states = st.sidebar.slider("Top states to display", 10, 25, 15)

# Apply filters
filtered = df.copy()

if selected_states:
    filtered = filtered[filtered["state"].isin(selected_states)]

# Access classification (simple, public-friendly)
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
# TOP KPI ROW (Make it “understandable”)
# -----------------------------
total_stations = len(filtered)
states_covered = filtered["state"].nunique()

# Ports (not stations): sum of EVSE counts
level2_ports = int(filtered["ev_level2_evse_num"].sum())
dc_fast_ports = int(filtered["ev_dc_fast_count"].sum())

# Avoid divide-by-zero
total_ports = max(level2_ports + dc_fast_ports, 1)
dc_share = round((dc_fast_ports / total_ports) * 100, 1)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Stations", f"{total_stations:,}", help="Station sites (locations).")
col2.metric("States covered", f"{states_covered}", help="How many states appear in this filtered view.")
col3.metric(
    "Everyday chargers (Level 2 ports)",
    f"{level2_ports:,}",
    help="Slower chargers used at destinations (work, shopping, home).",
)
col4.metric(
    "Road-trip fast chargers (DC Fast ports)",
    f"{dc_fast_ports:,}",
    help="Fast chargers often used on highways and quick stops.",
)

st.divider()

# -----------------------------
# SECTION 1: Fast vs Everyday (Public story)
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
# SECTION 2: Top states (clear, sortable)
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
# SECTION 3: Explore a state
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

    c1, c2, c3 = st.columns(3)
    c1.metric("Everyday chargers (Level 2 ports)", f"{lvl2:,}")
    c2.metric("Fast chargers (DC Fast ports)", f"{dcfc:,}")
    c3.metric("Fast-charger share", f"{state_dc_share}%", help="Fast ports / (fast + level 2 ports)")

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
    # MAP (Antarctica-proof)
    # -----------------------------
    if show_map:
        st.subheader("🗺️ Map of station locations")

        map_df = state_df.copy()

        # Force numeric coordinates
        map_df["latitude"] = pd.to_numeric(map_df["latitude"], errors="coerce")
        map_df["longitude"] = pd.to_numeric(map_df["longitude"], errors="coerce")
        map_df = map_df.dropna(subset=["latitude", "longitude"])

        if map_df.empty:
            st.warning("No valid coordinates available for this selection.")
        else:
            # Detect obvious swap (lat should be ~10..72; lon should be ~-170..-50 for US)
            lat_med = float(map_df["latitude"].median())
            lon_med = float(map_df["longitude"].median())

            looks_swapped = (-170 <= lat_med <= -50) and (10 <= lon_med <= 72)
            if looks_swapped:
                map_df = map_df.rename(columns={"latitude": "lon_tmp", "longitude": "latitude"})
                map_df = map_df.rename(columns={"lon_tmp": "longitude"})

            # Hard filter to US-ish bounds so we never end up in Antarctica
            map_df = map_df[
                map_df["latitude"].between(10, 72)
                & map_df["longitude"].between(-170, -50)
            ]

            # Public-friendly default: Contiguous US
            contiguous_only = st.checkbox("Show contiguous U.S. only (recommended)", value=True)
            if contiguous_only:
                map_df = map_df[
                    map_df["latitude"].between(24, 50)
                    & map_df["longitude"].between(-125, -66)
                ]

            if map_df.empty:
                st.warning("After cleaning coordinates, no points remain. Try widening filters.")
            else:
                # Keep map fast
                map_df = map_df.sample(min(len(map_df), 5000), random_state=42)

                # Center map on data
                center_lat = float(map_df["latitude"].median())
                center_lon = float(map_df["longitude"].median())

                fig_map = px.scatter_mapbox(
                    map_df,
                    lat="latitude",
                    lon="longitude",
                    hover_name="station_name",
                    hover_data={"city": True, "state": True, "ev_network": True},
                    zoom=3.3,
                    height=600,
                )
                fig_map.update_layout(
                    mapbox_style="open-street-map",
                    mapbox_center={"lat": center_lat, "lon": center_lon},
                    margin={"r": 0, "t": 0, "l": 0, "b": 0},
                )
                st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# -----------------------------
# SECTION 4: Download + transparency
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

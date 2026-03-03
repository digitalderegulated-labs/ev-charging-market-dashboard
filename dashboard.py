import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="US EV Charging Infrastructure Intelligence",
    page_icon="⚡",
    layout="wide",
)

# -----------------------------
# HEADER
# -----------------------------
st.title("⚡ US EV Charging Infrastructure Intelligence")
st.caption(
    "Live U.S. EV charging station data from the DOE AFDC (NREL) API. "
    "Designed for public clarity + portfolio credibility."
)

# -----------------------------
# LOAD DATA (API ONLY)
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

if df.empty:
    st.error("No data returned from the AFDC API.")
    st.stop()

# -----------------------------
# SAFE COLUMN HANDLING (NO CRASH)
# -----------------------------
def ensure_col(name: str, default):
    if name not in df.columns:
        df[name] = default

ensure_col("state", "")
ensure_col("city", "")
ensure_col("station_name", "")
ensure_col("access_code", "")
ensure_col("groups_with_access_code", "")
ensure_col("ev_network", "Unknown")
ensure_col("ev_level2_evse_num", 0)
ensure_col("ev_dc_fast_count", 0)

df["state"] = df["state"].astype(str).str.strip().str.upper()
df["city"] = df["city"].astype(str).str.strip()

df["ev_network"] = (
    df["ev_network"]
    .fillna("Unknown")
    .astype(str)
    .replace({"": "Unknown", "nan": "Unknown"})
)

for col in ["ev_level2_evse_num", "ev_dc_fast_count"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filters")

all_states = sorted([s for s in df["state"].dropna().unique() if s and s != "NAN"])
selected_states = st.sidebar.multiselect(
    "State(s)",
    options=all_states,
    default=[],
    help="Leave empty to show all U.S. states in the dataset.",
)

access_filter = st.sidebar.selectbox(
    "Access",
    options=["All", "Public", "Private"],
    index=0,
)

networks = sorted(df["ev_network"].unique().tolist())
network_filter = st.sidebar.selectbox(
    "Network",
    options=["All"] + networks,
    index=0,
)

top_n = st.sidebar.slider("Show top N", 5, 25, 15)

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
    filtered = filtered[filtered["ev_network"] == network_filter]

if filtered.empty:
    st.warning("No results match your filters. Try widening them in the sidebar.")
    st.stop()

# -----------------------------
# EXECUTIVE KPI ROW
# -----------------------------
total_stations = len(filtered)
states_covered = filtered["state"].nunique()

level2_ports = int(filtered["ev_level2_evse_num"].sum())
dc_fast_ports = int(filtered["ev_dc_fast_count"].sum())
total_ports = max(level2_ports + dc_fast_ports, 1)
dc_share = round((dc_fast_ports / total_ports) * 100, 1)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Stations (locations)", f"{total_stations:,}")
k2.metric("States covered", f"{states_covered:,}")
k3.metric("Everyday chargers (Level 2 ports)", f"{level2_ports:,}")
k4.metric("Road-trip fast chargers (DC Fast ports)", f"{dc_fast_ports:,}")

st.info(
    f"**Insight:**{dc_share}%** of ports are fast chargers. "
    "Higher fast-charger share typically supports better road-trip / corridor coverage."
)

st.divider()

# -----------------------------
# SECTION 1: CHARGER MIX
# -----------------------------
st.subheader("⚡ Charging speed mix")

mix_df = pd.DataFrame(
    {
        "Charger type": ["Everyday chargers (Level 2)", "Road-trip fast chargers (DC Fast)"],
        "Ports": [level2_ports, dc_fast_ports],
    }
)

fig_mix = px.bar(mix_df, x="Charger type", y="Ports", text="Ports")
fig_mix.update_layout(height=420, xaxis_title="", yaxis_title="Ports")
st.plotly_chart(fig_mix, use_container_width=True)

st.divider()

# -----------------------------
# SECTION 2: TOP STATES
# -----------------------------
st.subheader("🏁 Top states by station count")

state_counts = (
    filtered.groupby("state")
    .size()
    .reset_index(name="Stations")
    .sort_values("Stations", ascending=False)
)

fig_states = px.bar(
    state_counts.head(top_n),
    x="state",
    y="Stations",
    text="Stations",
)
fig_states.update_layout(height=450, xaxis_title="State", yaxis_title="Stations")
st.plotly_chart(fig_states, use_container_width=True)

st.divider()

# -----------------------------
# SECTION 3: TOP NETWORKS
# -----------------------------
st.subheader("🏢 Top charging networks (by station count)")

network_counts = (
    filtered["ev_network"]
    .value_counts()
    .reset_index()
)

network_counts.columns = ["Network", "Stations"]

# Market share for public-friendly insight
network_counts["Market Share %"] = (network_counts["Stations"] / network_counts["Stations"].sum() * 100).round(1)

fig_networks = px.bar(
    network_counts.head(top_n),
    x="Network",
    y="Stations",
    text="Market Share %",
)
fig_networks.update_traces(texttemplate="%{text}%", textposition="outside")
fig_networks.update_layout(height=520, xaxis_title="", yaxis_title="Stations")
st.plotly_chart(fig_networks, use_container_width=True)

st.divider()

# -----------------------------
# SECTION 4: TOP CITIES
# -----------------------------
st.subheader("🏙️ Top cities (by station count)")

# Create a safe city label
city_df = filtered.copy()
city_df["city"] = city_df["city"].replace({"": "Unknown", "nan": "Unknown"}).fillna("Unknown")

city_counts = (
    city_df.groupby(["state", "city"])
    .size()
    .reset_index(name="Stations")
    .sort_values("Stations", ascending=False)
)

fig_cities = px.bar(
    city_counts.head(top_n),
    x="city",
    y="Stations",
    text="Stations",
    hover_data=["state"],
)
fig_cities.update_layout(height=520, xaxis_title="City", yaxis_title="Stations")
st.plotly_chart(fig_cities, use_container_width=True)

st.divider()

# -----------------------------
# SECTION 5: DATA TABLE + DOWNLOAD
# -----------------------------
st.subheader("📥 Download the filtered dataset")
st.write("Download what you're seeing (after filters) for transparency or deeper analysis.")

st.download_button(
    "Download filtered data as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="ev_charging_filtered.csv",
    mime="text/csv",
)

with st.expander("Preview filtered data (first 200 rows)"):
    st.dataframe(filtered.head(200), use_container_width=True)

st.markdown("---")
st.caption("Built by Digital Deregulated Labs • Live federal infrastructure data via AFDC (NREL) API")


import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EV Market Intelligence Dashboard", layout="wide")

st.title("EV Charging Market Intelligence Dashboard")
st.markdown("Live data from U.S. Department of Energy AFDC.")

# Get API key securely
API_KEY = st.secrets["NREL_API_KEY"]

DATA_URL = (
    "https://developer.nrel.gov/api/alt-fuel-stations/v1.csv?"
    f"api_key={API_KEY}"
    "&fuel_type=ELEC"
    "&limit=all"
)

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    return df

df = load_data()

# Clean column names (NREL sometimes capitalizes)
df.columns = df.columns.str.lower()

total_stations = len(df)
total_states = df["state"].nunique()

col1, col2 = st.columns(2)
col1.metric("Total EV Charging Stations (US)", f"{total_stations:,}")
col2.metric("States Represented", total_states)

st.divider()

state_counts = df.groupby("state").size().reset_index(name="Stations")
state_counts = state_counts.sort_values("Stations", ascending=False)

st.subheader("Top 15 States by EV Charging Infrastructure")

fig = px.bar(
    state_counts.head(15),
    x="state",
    y="Stations",
    text="Stations"
)

fig.update_layout(height=500)

st.plotly_chart(fig, use_container_width=True)

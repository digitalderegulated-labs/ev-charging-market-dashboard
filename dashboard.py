import streamlit as st
import pandas as pd
import plotly.express as px

st.title("EV Charging Market Dashboard")

df = pd.read_csv("ev_data.csv")
df = df[df["Fuel Type Code"] == "ELEC"]

# Group by state
state_counts = df.groupby("State").size().reset_index(name="Stations")
state_counts = state_counts.sort_values("Stations", ascending=False)

st.subheader("Top 10 States by EV Charging Stations")
top10 = state_counts.head(10)

fig = px.bar(top10, x="State", y="Stations",
             title="Top 10 States by EV Charging Stations")

st.plotly_chart(fig)

# State selector
st.subheader("Explore Individual State")

selected_state = st.selectbox("Choose a State", state_counts["State"])

state_data = df[df["State"] == selected_state]

st.write(f"Total Stations in {selected_state}: {len(state_data)}")

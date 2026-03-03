import streamlit as st
import pandas as pd
import plotly.express as px

st.title("EV Charging Market Dashboard")

df = pd.read_csv("ev_data.csv")

df = df[df["Fuel Type Code"] == "ELEC"]

state_counts = df.groupby("State").size().reset_index(name="Stations")

fig = px.bar(state_counts, x="State", y="Stations",
             title="EV Charging Stations by State")

st.plotly_chart(fig)
# EV Charging Network Competitive Intelligence Platform

Live App: https://ev-charging-market-dashboard.streamlit.app/

## What this is
A live competitive intelligence dashboard for U.S. EV charging networks using federal infrastructure data from the DOE/NREL AFDC API.

## What it delivers
- Network market share (stations)
- Market concentration (HHI)
- DC Fast strategy by network (when port fields are available)
- State-level market leaders and dominance
- Geographic footprint mapping
- Whitespace heuristic to flag expansion targets

## Why it matters
This turns public infrastructure data into actionable competitive insight for:
- charging network expansion teams
- utility partnership / corridor planning
- market entry & benchmarking
- investment prioritization

## Tech
Python • Streamlit • Pandas • Plotly • NREL/AFDC API

## Security
API key stored in Streamlit Secrets (`NREL_API_KEY`), not in GitHub.

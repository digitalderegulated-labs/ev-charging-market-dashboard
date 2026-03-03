# ⚡ US EV Charging Infrastructure Dashboard

**Live dashboard:** https://ev-charging-market-dashboard.streamlit.app/

This project pulls **live EV charging infrastructure data** from the U.S. Department of Energy’s **AFDC (NREL) API** and turns it into a clean, public-friendly dashboard.

## What it shows (in plain English)

- **Stations:** how many charging locations exist
- **Everyday chargers (Level 2):** best for longer stops (work/shopping/home)
- **Road-trip fast chargers (DC Fast):** best for quick top-ups on the go
- **Top states by infrastructure**
- **Network landscape** (top providers by station count)
- **Interactive map** of locations (optional)
- **Downloadable filtered dataset**

## Why it’s useful

This dashboard is designed to be understandable for the **general public**, while still demonstrating real-world skills in:
- live API data pipelines
- data cleaning + resilience (no-crash handling)
- interactive visualization
- dashboard UX and storytelling

## Tech stack

- Python
- Streamlit
- Pandas
- Plotly
- AFDC / NREL API

## Running locally

1) Install dependencies:
```bash
pip install -r requirements.txt

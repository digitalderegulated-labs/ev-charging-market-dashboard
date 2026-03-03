# ⚡ US EV Charging Infrastructure Intelligence Dashboard

**Live dashboard:** https://ev-charging-market-dashboard.streamlit.app/

A public, interactive dashboard that pulls **live U.S. EV charging infrastructure data** from the U.S. Department of Energy’s **AFDC (NREL) Alternative Fuel Stations API** and turns it into a clean, explorable market view.

This project demonstrates how raw federal infrastructure data can be transformed into a **production-ready analytics product** — from API ingestion and normalization to interactive visualization and deployment.

---

## What it shows (plain English)

- **Total EV charging locations (U.S.)** and how widely they’re distributed across states  
- **Top states** by charging infrastructure concentration  
- **Charging power mix** (Level 2 vs DC Fast) to compare “everyday charging” vs “road-trip charging”  
- **Network landscape** (top providers by station count)  
- **State drill-down** (pick any state to see key stats)  
- **Map view (optional)** for geographic distribution  
- **Downloadable dataset** based on the filters you choose

---

## Why it’s useful

This project balances public clarity with professional-grade implementation:

- **Live API data ingestion** (NREL/AFDC)  
- **Data cleaning + normalization** (consistent column handling across API outputs)  
- **Interactive exploration** (filters, drilldowns, state-level views)  
- **Insight-oriented visualization** (not just charts — market-relevant framing)  
- **Production deployment** on Streamlit Community Cloud

---

## Tech stack

- **Python**
- **Streamlit**
- **Pandas**
- **Plotly**
- **AFDC / NREL Alternative Fuel Stations API**

---

## Data source

AFDC Alternative Fuel Stations API (NREL): https://developer.nrel.gov/

---

## Running locally

### 1) Clone the repo

```bash
git clone https://github.com/digitalderegulated-labs/ev-charging-market-dashboard.git
cd ev-charging-market-dashboard

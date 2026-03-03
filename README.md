# ⚡ US EV Charging Infrastructure Intelligence Dashboard

🔗 **Live Dashboard:**  
https://ev-charging-market-dashboard.streamlit.app/

This dashboard pulls **live EV charging infrastructure data** from the U.S. Department of Energy’s **AFDC (NREL) API** and turns it into an interactive, public-facing analytics product.

It demonstrates how raw federal infrastructure data can be **fetched via API**, **cleaned**, **modeled**, and **visualized** into actionable market insight.

---

## What it shows (in plain English)

- **Total EV charging locations (US)** and how widely distributed they are across states
- **Top states** by charging infrastructure concentration
- **Charging power mix** (Level 2 vs DC Fast) to understand “everyday charging” vs “road-trip charging”
- **Network landscape** (top providers by station count)
- **State drill-down** for quick “market snapshot” by state
- **Map view** (optional) for geographic distribution
- **Downloadable dataset** based on your current filters

---

## Why it’s useful

This dashboard is designed to be understandable to the general public *while still demonstrating real-world technical and analytical skills*:

- Live API data ingestion (federal infrastructure dataset)
- Data cleaning + schema normalization (consistent column handling)
- Interactive exploration and filtering (market segmentation by state/network/access/type)
- Insight-oriented visualization and storytelling (not just charts)
- Production deployment on Streamlit Community Cloud

---

## Tech Stack

- **Python**
- **Streamlit**
- **Pandas**
- **Plotly**
- **AFDC / NREL Alternative Fuel Stations API**

---

## Running locally

### 1) Clone the repo
```bash
git clone https://github.com/digitalderegulated-labs/ev-charging-market-dashboard.git
cd ev-charging-market-dashboard

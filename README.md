# ⚡ US EV Charging Infrastructure Intelligence Dashboard  
### A Digital Deregulated Labs Project

🔗 **Live Application:**  
https://ev-charging-market-dashboard.streamlit.app/

An interactive analytics dashboard built on live U.S. EV charging infrastructure data from the U.S. Department of Energy’s AFDC (NREL) API.

This project demonstrates how public infrastructure data can be ingested, normalized, and transformed into a clean, deployable analytics product.

---

## Overview

The U.S. EV charging market is expanding rapidly due to federal incentives, utility partnerships, and private network investment.  

This dashboard provides a structured view of that infrastructure landscape, turning raw federal data into clear, explorable insight.

It balances accessibility for public audiences with production-grade engineering implementation.

---

## What the dashboard provides

- National EV charging station count
- Infrastructure concentration by state
- Charging power mix (Level 2 vs DC Fast)
- Network landscape (top providers)
- State-level drilldown analysis
- Optional interactive geographic mapping
- Downloadable filtered dataset

---

## Why this project matters

This dashboard reflects real-world implementation skills:

- Live API integration (federal infrastructure dataset)
- Data cleaning and schema normalization
- Interactive filtering and drilldown views
- Insight-focused visualization (not just charts)
- Production deployment with secure configuration management
- Clean UI/UX framing for non-technical audiences

It demonstrates the ability to transform public data into decision-ready infrastructure intelligence.

---

## Technology Stack

- Python
- Streamlit
- Pandas
- Plotly
- AFDC / NREL Alternative Fuel Stations API
- Streamlit Community Cloud (deployment)

---

## Data Source

AFDC Alternative Fuel Stations API (NREL)  
https://developer.nrel.gov/

---

## Project Structure

- `dashboard.py` – main application logic
- `requirements.txt` – dependency configuration
- `.streamlit/config.toml` – UI theme configuration

---

## About Digital Deregulated Labs

Digital Deregulated Labs focuses on building analytics tools and infrastructure intelligence platforms across energy, utilities, and regulated markets.

This dashboard serves as a live demonstration of applied data engineering and energy market analytics.

---

## License

MIT

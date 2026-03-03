# ⚡ US EV Charging Infrastructure Intelligence Dashboard

🔗 **Live Application:**  
https://ev-charging-market-dashboard.streamlit.app/

An interactive analytics dashboard built on live U.S. EV charging infrastructure data from the U.S. Department of Energy’s AFDC (NREL) API.

This project demonstrates how public infrastructure data can be ingested, normalized, and transformed into a clean, deployable analytics product.

---

## What the dashboard provides

- National EV charging station count
- Infrastructure concentration by state
- Charging power mix (Level 2 vs DC Fast)
- Network landscape (top providers)
- State-level drilldown analysis
- Interactive geographic mapping
- Downloadable filtered dataset

---

## Why this project matters

This dashboard reflects real-world implementation skills:

- Live API integration (federal infrastructure dataset)
- Data cleaning and schema normalization
- Interactive filtering and drilldown views
- Insight-focused visualization (not just charts)
- Cloud deployment with secure configuration

It is designed to be accessible to non-technical viewers while still demonstrating production-ready engineering practices.

---

## Technology

- Python
- Streamlit
- Pandas
- Plotly
- AFDC / NREL Alternative Fuel Stations API

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

## License

MIT

# Digital Deregulated Labs – Operational Intelligence Dashboards

This repository contains a working dashboard built as part of my Digital Deregulated Labs portfolio.

The goal of these projects is to demonstrate how complex operational data can be translated into clear,
decision-friendly dashboards for both technical users and non-experts.

These dashboards include short "Insights" sections that explain what the data means and why it matters.

Note: These insights are examples of how an analyst might interpret the data. They are included for educational
and demonstration purposes and should not be considered formal operational guidance.

# ⚡ US EV Charging Infrastructure Intelligence Dashboard  
### A Digital Deregulated Labs Project

🔗 **Live Application:**  
https://ev-charging-market-dashboard.streamlit.app/

An interactive analytics dashboard built on live U.S. EV charging infrastructure data from the U.S. Department of Energy’s AFDC (NREL) Alternative Fuel Stations API.

This project demonstrates how public infrastructure data can be ingested, normalized, and transformed into a clean, deployable analytics product.

---

## Built for

- EV charging developers evaluating expansion markets and infrastructure density
- Energy suppliers and utilities targeting EV load growth
- Analysts benchmarking charging network footprint by state and city

---

## What the dashboard provides

- National EV charging station count
- Infrastructure concentration by state
- Charging speed mix (Level 2 vs DC Fast)
- Network landscape (top providers + market share)
- City concentration (top cities by station count)
- Downloadable filtered dataset (transparency + further analysis)

---

## Why this project matters

This dashboard reflects real-world implementation skills:

- Live API integration (federal infrastructure dataset)
- Data cleaning and schema normalization
- Interactive filtering and drilldown views
- Insight-focused visualization (not just charts)
- Production deployment with secure configuration management

It demonstrates the ability to transform public data into decision-ready infrastructure intelligence.

---

## Technology Stack

- Python
- Streamlit
- Pandas
- Plotly
- Streamlit Community Cloud (deployment)

---

## Data Source

AFDC Alternative Fuel Stations API (NREL)  
https://developer.nrel.gov/

---

## Project Structure

- `dashboard.py` – main application logic
- `requirements.txt` – dependency configuration
- `.streamlit/config.toml` – UI theme configuration (optional)

---

## About Digital Deregulated Labs

Digital Deregulated Labs focuses on building analytics tools and infrastructure intelligence platforms across technology, energy, and healthcare.

This dashboard serves as a live demonstration of applied data engineering and energy market analytics.

---

## License

MIT

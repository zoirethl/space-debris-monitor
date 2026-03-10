🛰️ Space Debris Monitoring System

> A live data engineering project tracking orbital congestion, debris density, and space safety risks — built as part of a career transition from Mechanical Maintenance Engineering into Data Engineering.
> 
[![Weekly Space Data Update](https://github.com/zoirethl/space-debris-monitor/actions/workflows/update_data.yml/badge.svg?branch=main)](https://github.com/zoirethl/space-debris-monitor/actions/workflows/update_data.yml)
---

## 📌 Overview

Earth's orbit is no longer empty. Decades of launches have created a dense and growing population of satellites, debris, and inactive payloads. This project retrieves, processes, and visualizes real-time orbital data to answer three core questions:

- **How did we get here?** — Exponential growth of orbital objects over the last 20 years
- **Where are the risks?** — Congestion hotspots in Low Earth Orbit (LEO)
- **Who is responsible?** — Country-level breakdown of objects in orbit

This project started as a Tableau dashboard (exploratory data storytelling) and is now evolving into a live Python + Streamlit application with automated data ingestion.

---

## 🚀 Live App Features

- Real-time KPIs — total objects in orbit, active satellites vs. debris ratio
- Orbital distribution — LEO / MEO / GEO breakdown with interactive charts
- Top 10 countries — which nations have the most objects in orbit
- Timeline — debris growth over time by launch year
- Interactive filters — filter by country, object type, and orbit
- Satellite search — look up any object by name (e.g., STARLINK, ISS, NOAA)
- Debris inventory — sortable, searchable table of tracked objects

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
|  Data Source | [Space-Track.org](https://www.space-track.org) (official US Space Surveillance Network) |
| Data Pipeline | Python + `requests` + `pandas` |
| Automation | GitHub Actions (weekly cron job) |
| App Framework | `streamlit` |
| Visualization | `plotly` |
| Language | Python 3.12 |

---

Data is fetched weekly via an automated GitHub Actions workflow:

```
fetch_data.py (local or GitHub Actions)
    → authenticates with Space-Track.org API
    → downloads active satellites + debris as CSV
    → commits data/active_satellites.csv + data/debris.csv to repo
    → Streamlit Cloud reads updated CSVs on next load
```

To run the pipeline manually:
```bash
python fetch_data.py
```

Requires credentials stored in `.streamlit/secrets.toml`:
```toml
SPACETRACK_USER = "your_email@example.com"
SPACETRACK_PASS = "your_password"
```

---

## 📁 Project Structure

```
space-debris-monitor/
│
├── space_app.py              # Main Streamlit application
├── fetch_data.py             # Data pipeline — fetches from Space-Track.org
├── requirements.txt          # Python dependencies
├── data/
│   ├── active_satellites.csv # Latest active payload data
│   ├── debris.csv            # Latest debris data
│   └── last_updated.txt      # Timestamp of last pipeline run
├── .github/
│   └── workflows/
│       └── update_data.yml   # GitHub Actions weekly automation
└── README.md
```

---

## ⚙️ Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/zoirethl/space-debris-monitor.git
cd space-debris-monitor
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your Space-Track credentials
Create `.streamlit/secrets.toml`:
```toml
SPACETRACK_USER = "your_email@example.com"
SPACETRACK_PASS = "your_password"
```

### 4. Fetch data and run the app
```bash
python fetch_data.py
streamlit run space_app.py
```
---

## 📦 Requirements

```
streamlit
pandas
requests
plotly
```

---

## 🗺️ Roadmap

This project is actively evolving. Planned additions:

- [x] Space-Track.org API integration with authentication
- [x] Automated weekly data pipeline via GitHub Actions
- [x] LEO / MEO / GEO orbital distribution charts
- [x] Top 10 countries by objects in orbit
- [x] Debris growth timeline by launch year
- [x] Interactive filters by country and object type
- [ ] Collision probability estimates using proximity calculations
- [ ] Historical trend comparison year-over-year
- [ ] Email/Slack alert when debris count crosses threshold

---

## 📊 Previous Version — Tableau Dashboard

The original version of this analysis was built in Tableau Public and focused on data storytelling:

- Orbital growth time-series (20-year trend)
- Geographic density mapping by launch site
- Country responsibility breakdown
- Risk projection narrative

*Data source: [Space-Track.org](https://www.space-track.org) + open-source satellite datasets*

---

## 👩‍💻 About

This project reflects both worlds: the systems thinking and operational mindset from years managing industrial assets, applied to a data problem that has real-world safety consequences.

**Current skills in practice:** Python · pandas · Streamlit · Plotly · GitHub Actions · REST APIs · Tableau

---

## 📄 License

MIT License — feel free to fork and build on this.

---

*If you find this useful or want to collaborate, feel free to open an issue or reach out.*

[![Weekly Space Data Update](https://github.com/zoirethl/space-debris-monitor/actions/workflows/update_data.yml/badge.svg?branch=main)](https://github.com/zoirethl/space-debris-monitor/actions/workflows/update_data.yml)

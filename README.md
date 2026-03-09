# 🛰️ Space Debris Monitoring System

> A live data engineering project tracking orbital congestion, debris density, and space safety risks.
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

- **Real-time data extraction** from [Celestrak](https://celestrak.org) via TLE files
- **KPI dashboard** — total objects in orbit, active satellites vs. debris ratio
- **Satellite search** — look up any object by name (e.g., STARLINK, ISS, NOAA) and inspect its catalog data
- **Debris inventory** — filterable table of the top tracked debris objects

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Data Source | [Celestrak NORAD](https://celestrak.org) (live TLE feed) |
| Orbital Calculations | `skyfield` |
| Data Processing | `pandas` |
| App Framework | `streamlit` |
| Language | Python 3.x |

---

## 📁 Project Structure

```
space-debris-monitor/
│
├── app.py               # Main Streamlit application
├── requirements.txt     # Python dependencies
└── README.md
```

---

## ⚙️ Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/space-debris-monitor.git
cd space-debris-monitor
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📦 Requirements

```
streamlit
pandas
skyfield
```

---

## 🗺️ Roadmap

This project is actively evolving. Planned additions:

- [ ] Orbital altitude distribution charts (LEO / MEO / GEO breakdown)
- [ ] Time-series visualization of debris growth over the last 20 years
- [ ] Country-level responsibility breakdown (mirroring the Tableau version)
- [ ] Collision probability estimates using proximity calculations with `skyfield`
- [ ] Automated daily data pipeline with local storage

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

**Current skills in practice:** Python · pandas · Streamlit · Tableau · SQL · Data Pipeline design (learning)

---

## 📄 License

MIT License — feel free to fork and build on this.

---

*If you find this useful or want to collaborate, feel free to open an issue or reach out.*

[![Weekly Space Data Update](https://github.com/zoirethl/space-debris-monitor/actions/workflows/update_data.yml/badge.svg?branch=main)](https://github.com/zoirethl/space-debris-monitor/actions/workflows/update_data.yml)

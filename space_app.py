import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Space Safety Engineer", layout="wide")

st.title("🛰️ Space Debris Monitoring System")

@st.cache_data(ttl=3600)

def get_space_data():
    try:
        active_df = pd.read_csv('data/active_satellites.csv')
        debris_df = pd.read_csv('data/debris.csv')
        return active_df, debris_df
    except FileNotFoundError:
        st.error("Data files not found. Run fetch_data.py first.")
        return pd.DataFrame(), pd.DataFrame()

# Mostrar fecha de última actualización
try:
    with open('data/last_updated.txt') as f:
        last_updated = f.read()
    st.caption(f"📅 Data last updated: {last_updated}")
except:
    pass

with st.spinner('Loading orbital data...'):
    active_sats, debris_sats = get_space_data()

# --- (ETL: Transform) ---
total_objects = len(active_sats) + len(debris_sats)
pct_debris = (len(debris_sats) / total_objects) * 100

# Main KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Objects in Orbit", total_objects)
col2.metric("Active Satellites", len(active_sats))
col3.metric("Debris", len(debris_sats), delta=f"{pct_debris:.1f}% of total", delta_color="inverse")

# --- Search Bar ---
st.subheader("Satellite Search")
search = st.text_input("Input a Satellite name to evaluate it surroundings (ej: STARLINK, ISS, NOAA):")

if search:
    matches = active_sats[active_sats['OBJECT_NAME'].str.contains(search.upper(), na=False)]
    if not matches.empty:
        target = matches.iloc[0]
        st.write(f"### 🛡️ Report for: {target['OBJECT_NAME']}")
        st.info(f"ID Catalog: {target['NORAD_CAT_ID']} | Epoch: {target['EPOCH']}")
    else:
        st.warning("Object not found")

if st.checkbox("Check debris inventory (Top 100)"):
    st.table(debris_sats[['OBJECT_NAME', 'NORAD_CAT_ID']].head(100))
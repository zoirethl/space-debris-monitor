import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Space Safety Engineer", layout="wide")

st.title("🛰️ Space Debris Monitoring System")

@st.cache_data(ttl=3600)
def get_space_data(group):
    url = f'https://celestrak.org/NORAD/elements/gp.php?GROUP={group}&FORMAT=tle'
    for intento in range(3):  # intenta hasta 3 veces
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            df['type'] = group
            return df
        except Exception as e:
            if intento == 2: 
                st.error(f"No se pudo conectar a Celestrak después de 3 intentos: {e}")
                return pd.DataFrame()  
            import time
            time.sleep(5)  

    responses = requests.get(url)
    from io import StringIO
    df = pd.read_csv(StringIO(response.text))
    df['type'] = group
    return df 

# --- (ETL: Extract) ---
with st.spinner('Extracting and transforming orbital data...'):
    active_sats = get_space_data('active')
    debris_sats = get_space_data('debris')

# --- (ETL: Transform) ---
total_objects = len(active_sats) + len(debris_sats)
pct_debris = (len(debris_sats) / total_objects) * 100


if active_sats.empty or debris_sats.empty:
    st.warning("⚠️ Could not load data from Celestrak. Please refresh in a few minutes.")
    st.stop()
    
# Main KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Objects in Orbit", total_objects)
col2.metric("Active Satellites", len(active_sats))
col3.metric("Debris", len(debris_sats), delta=f"{pct_debris:.1f}% of total", delta_color="inverse")

# --- Search Bar ---
st.subheader("Satellite Search")
search = st.text_input("Input a Satellite name to evaluate it surroundings (ej: STARLINK, ISS, NOAA):")

if search:
    # Only filter matching names
    matches = active_sats[active_sats['name'].str.contains(search.upper(), na=False)]
    if not matches.empty:
        target = matches.iloc[0]
        st.write(f"### 🛡️ Report for: {target['name']}")
        st.info(f"ID Catalog: {target['catalog_number']} | Age: {target['epoch']}")
        
        # To add Skyfield distance calculations later
    else:
        st.warning("Object not found")

# Shows raw data
if st.checkbox("Check debris inventory (Top 100)"):
    st.table(debris_sats[['name', 'catalog_number']].head(100))
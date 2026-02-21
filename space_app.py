import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Space Safety Engineer", layout="wide")

st.title("🛰️ Space Debris Monitoring System")

@st.cache_data(ttl=3600)
def get_space_data():
    import time
    from io import StringIO

    credentials = {
        'identity': st.secrets["SPACETRACK_USER"],
        'password': st.secrets["SPACETRACK_PASS"]
    }
    
    session = requests.Session()
    
    # Login
    login_url = 'https://www.space-track.org/ajaxauth/login'
    response = session.post(login_url, data=credentials, timeout=30)
    
    if response.status_code != 200:
        st.error(f"Login failed. Status: {response.status_code}")
        st.code(response.text[:500])
        return pd.DataFrame(), pd.DataFrame()
    
       
    # Query — todos los objetos en órbita con datos básicos
    base_url = 'https://www.space-track.org/basicspacedata/query/class/gp'
    
    # Satélites activos (OBJECT_TYPE = PAYLOAD, DECAYED = 0)
    active_url = f'{base_url}/OBJECT_TYPE/PAYLOAD/DECAYED/0/orderby/NORAD_CAT_ID/format/csv'
    # Debris (OBJECT_TYPE = DEBRIS, DECAYED = 0)
    debris_url = f'{base_url}/OBJECT_TYPE/DEBRIS/DECAYED/0/orderby/NORAD_CAT_ID/format/csv'
    
    active_response = session.get(active_url, timeout=60)

    #Debug
    st.write(f"Active response status: {active_response.status_code}")
    st.code(active_response.text[:300]) 

    time.sleep(2)  # Space-Track pide respetar rate limits
    debris_response = session.get(debris_url, timeout=60)
    
    try:
        active_df = pd.read_csv(StringIO(active_response.text))
        active_df['type'] = 'active'
    except Exception as e:
        st.error(f"Error parseando active: {e}")
        return pd.DataFrame(), pd.DataFrame()

    try:
        debris_df = pd.read_csv(StringIO(debris_response.text))
        debris_df['type'] = 'debris'
    except Exception as e:
        st.error(f"Error parseando debris: {e}")
        return pd.DataFrame(), pd.DataFrame()
    
    session.get('https://www.space-track.org/ajaxauth/logout')  # buena práctica
    
    return active_df, debris_df

# --- (ETL: Extract) ---
with st.spinner('Connecting to Space-Track.org...'):
    active_sats, debris_sats = get_space_data()

if active_sats.empty or debris_sats.empty:
    st.warning("⚠️ Could not load data from Space-Track. Please refresh in a few minutes.")
    st.stop()

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
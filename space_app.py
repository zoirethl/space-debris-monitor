import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Space Safety Engineer", layout="wide")

# ── CSS para tarjetas y separadores de sección ──────────────────────────────
st.markdown("""
<style>
    .card {
        background-color: #1a1a2e;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
        border: 1px solid #2e2e4e;
    }
    .section-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #F37FDF;
        margin-bottom: 8px;
    }
    div[data-testid="stMetric"] {
        background-color: #1a1a2e;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #2e2e4e;
    }
</style>
""", unsafe_allow_html=True)


st.title("🛰️ Space Debris Monitoring System")

@st.cache_data(ttl=3600)

def get_space_data():
    try:
        active_df = pd.read_csv('data/active_satellites.csv')
        debris_df = pd.read_csv('data/debris.csv')
        active_df['type'] = 'active' 
        debris_df['type'] = 'debris'
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
st.markdown('<div class="card"><div class="section-title">Overview</div></div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
col1.metric("Objects in Orbit", total_objects)
col2.metric("Active Satellites", len(active_sats))
col3.metric("Debris", len(debris_sats), delta=f"{pct_debris:.1f}% of total", delta_color="inverse")

st.divider()

# --- Search Bar ---
st.markdown('<div class="card"><div class="section-title">🔍 Satellite Search</div></div>', unsafe_allow_html=True)

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

st.divider()


# ---- Orbital altitude distribution charts (LEO / MEO / GEO breakdown) ----
st.markdown('<div class="card"><div class="section-title">Orbital Altitude Distribution</div></div>', unsafe_allow_html=True)

st.caption("""
**LEO** — Below 2,000 km. Highest debris density and collision risk.  
**MEO** — 2,000 to 35,786 km. GPS and navigation satellites.  
**GEO** — ~35,786 km. Weather and TV satellites, fixed over one point on Earth.
""")

def classify_orbit(mean_motion):
    if mean_motion >= 11.25:
        return 'LEO'
    elif mean_motion >= 2.0:
        return 'MEO'
    else:
        return 'GEO'

all_objects = pd.concat([active_sats, debris_sats])
all_objects['orbit_type'] = all_objects['MEAN_MOTION'].apply(classify_orbit)

orbit_counts = all_objects.groupby(['orbit_type','type']).size().reset_index(name='count')

col_pie, col_bar = st.columns(2)

with col_pie:
    fig_pie = px.pie(
        orbit_counts.groupby('orbit_type')['count'].sum().reset_index(),
        values='count',
        names='orbit_type',
        title='All Objects by Orbit Type',
        color='orbit_type',
        color_discrete_map={'LEO': "#F37FDF", 'MEO': "#878FF8", 'GEO': "#74E7C9"},
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_bar:
    fig_bar = px.bar(
        orbit_counts,
        x='orbit_type',
        y='count',
        color='type',
        title='Active Satellites vs Debris by Orbit',
        color_discrete_map={'active': '#878FF8', 'debris': '#F37FDF'},
        labels={'orbit_type': 'Orbit Type', 'count': 'Objects', 'type': 'Category'},
        barmode='group'
    )
    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig_bar, use_container_width=True)
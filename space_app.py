import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Space Debris Monitor",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Catppuccin Mocha palette ─────────────────────────────────────────────────
# Base: #1e1e2e | Surface: #313244 | Overlay: #45475a
# Pink: #f38ba8 | Mauve: #cba6f7 | Blue: #89b4fa
# Teal: #94e2d5 | Green: #a6e3a1 | Peach: #fab387
# Text: #cdd6f4 | Subtext: #a6adc8

MOCHA = {
    "base":    "#1e1e2e",
    "surface": "#313244",
    "overlay": "#45475a",
    "pink":    "#f38ba8",
    "mauve":   "#cba6f7",
    "blue":    "#89b4fa",
    "teal":    "#94e2d5",
    "green":   "#a6e3a1",
    "peach":   "#fab387",
    "text":    "#cdd6f4",
    "subtext": "#a6adc8",
}

st.markdown(f"""
<style>
    /* App background */
    .stApp {{ background-color: {MOCHA['base']}; }}

    /* Cards */
    .card {{
        background-color: {MOCHA['surface']};
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 8px;
        border: 1px solid {MOCHA['overlay']};
    }}
    .section-title {{
        font-size: 1.1rem;
        font-weight: 700;
        color: {MOCHA['mauve']};
        margin-bottom: 4px;
        letter-spacing: 0.03em;
    }}
    .section-desc {{
        font-size: 0.85rem;
        color: {MOCHA['subtext']};
        margin-bottom: 0;
    }}

    /* Metric cards */
    div[data-testid="stMetric"] {{
        background-color: {MOCHA['surface']};
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid {MOCHA['overlay']};
    }}
    div[data-testid="stMetricLabel"] p {{ color: {MOCHA['subtext']} !important; }}
    div[data-testid="stMetricValue"]  {{ color: {MOCHA['text']} !important; }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {MOCHA['surface']};
        border-right: 1px solid {MOCHA['overlay']};
    }}

    /* Divider */
    hr {{ border-color: {MOCHA['overlay']} !important; }}

    /* General text */
    p, li, label {{ color: {MOCHA['text']}; }}
</style>
""", unsafe_allow_html=True)


# ── Data loading ─────────────────────────────────────────────────────────────
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

def classify_orbit(mean_motion):
    if mean_motion >= 11.25:
        return 'LEO'
    elif mean_motion >= 2.0:
        return 'MEO'
    else:
        return 'GEO'

with st.spinner('Loading orbital data...'):
    active_sats, debris_sats = get_space_data()

if active_sats.empty or debris_sats.empty:
    st.warning("⚠️ Could not load data. Run fetch_data.py first.")
    st.stop()

all_objects = pd.concat([active_sats, debris_sats], ignore_index=True)
all_objects['orbit_type'] = all_objects['MEAN_MOTION'].apply(classify_orbit)

# Parse launch year safely
if 'LAUNCH_DATE' in all_objects.columns:
    all_objects['launch_year'] = pd.to_datetime(
        all_objects['LAUNCH_DATE'], errors='coerce'
    ).dt.year
elif 'EPOCH' in all_objects.columns:
    all_objects['launch_year'] = pd.to_datetime(
        all_objects['EPOCH'], errors='coerce'
    ).dt.year


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding: 12px 0 20px 0;'>
        <div style='font-size:2.2rem;'>🛰️</div>
        <div style='font-size:1.1rem; font-weight:700; color:{MOCHA["mauve"]};'>Space Debris Monitor</div>
        <div style='font-size:0.8rem; color:{MOCHA["subtext"]}; margin-top:4px;'>Powered by Space-Track.org</div>
    </div>
    """, unsafe_allow_html=True)

    try:
        with open('data/last_updated.txt') as f:
            last_updated = f.read()
        st.caption(f"📅 Last updated: {last_updated}")
    except:
        pass

    st.divider()
    st.markdown(f"<div style='color:{MOCHA['mauve']}; font-weight:600; margin-bottom:8px;'>🔭 What is this?</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='font-size:0.82rem; color:{MOCHA["subtext"]}; line-height:1.6;'>
    Earth's orbit contains <b style='color:{MOCHA["text"]};'>57,000+ tracked objects</b> —
    active satellites, rocket bodies, and debris from decades of launches.<br><br>
    This app tracks where they are, who put them there, and how the problem has grown over time.
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown(f"<div style='color:{MOCHA['mauve']}; font-weight:600; margin-bottom:8px;'>🎛️ Filters</div>", unsafe_allow_html=True)

    countries = sorted(all_objects['COUNTRY_CODE'].dropna().unique().tolist())
    selected_countries = st.multiselect(
        "Filter by Country",
        options=countries,
        default=[],
        placeholder="All countries"
    )

    orbit_options = ['LEO', 'MEO', 'GEO']
    selected_orbits = st.multiselect(
        "Filter by Orbit",
        options=orbit_options,
        default=[],
        placeholder="All orbits"
    )

    object_types = ['active', 'debris']
    selected_types = st.multiselect(
        "Filter by Object Type",
        options=object_types,
        default=[],
        placeholder="All types"
    )

# Apply filters
filtered = all_objects.copy()
if selected_countries:
    filtered = filtered[filtered['COUNTRY_CODE'].isin(selected_countries)]
if selected_orbits:
    filtered = filtered[filtered['orbit_type'].isin(selected_orbits)]
if selected_types:
    filtered = filtered[filtered['type'].isin(selected_types)]

is_filtered = bool(selected_countries or selected_orbits or selected_types)
filter_note = " *(filtered)*" if is_filtered else ""


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<h1 style='color:{MOCHA["text"]}; margin-bottom:4px;'>🛰️ Space Debris Monitoring System</h1>
<p style='color:{MOCHA["subtext"]}; font-size:0.95rem; margin-top:0;'>
    Real-time orbital data from the US Space Surveillance Network · Updated weekly
</p>
""", unsafe_allow_html=True)

st.divider()


# ── KPIs ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="card">
    <div class="section-title">📊 Overview{filter_note}</div>
    <div class="section-desc">Total tracked objects currently in Earth's orbit.</div>
</div>
""", unsafe_allow_html=True)

total  = len(filtered)
active = len(filtered[filtered['type'] == 'active'])
debris = len(filtered[filtered['type'] == 'debris'])
pct    = (debris / total * 100) if total > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Objects",      f"{total:,}")
col2.metric("Active Satellites",  f"{active:,}")
col3.metric("Debris",             f"{debris:,}", delta=f"{pct:.1f}% of total", delta_color="inverse")
col4.metric("LEO Objects",        f"{len(filtered[filtered['orbit_type']=='LEO']):,}")

st.divider()


# ── Orbital Distribution ──────────────────────────────────────────────────────
st.markdown(f"""
<div class="card">
    <div class="section-title">🌍 Orbital Altitude Distribution</div>
    <div class="section-desc">
        <b>LEO</b> (Low Earth Orbit) — below 2,000 km. Most satellites and debris live here. Highest collision risk.<br>
        <b>MEO</b> (Medium Earth Orbit) — 2,000–35,786 km. GPS and navigation satellites.<br>
        <b>GEO</b> (Geostationary Orbit) — ~35,786 km. Weather and TV satellites, appear fixed over one point.
    </div>
</div>
""", unsafe_allow_html=True)

orbit_counts = filtered.groupby(['orbit_type', 'type']).size().reset_index(name='count')

col_pie, col_bar = st.columns(2)

orbit_colors = {'LEO': MOCHA['pink'], 'MEO': MOCHA['mauve'], 'GEO': MOCHA['teal']}
type_colors  = {'active': MOCHA['blue'], 'debris': MOCHA['pink']}

with col_pie:
    fig_pie = px.pie(
        orbit_counts.groupby('orbit_type')['count'].sum().reset_index(),
        values='count', names='orbit_type',
        title='All Objects by Orbit Type',
        color='orbit_type', color_discrete_map=orbit_colors,
        hole=0.45
    )
    fig_pie.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color=MOCHA['text'], title_font_color=MOCHA['mauve'],
        legend=dict(bgcolor='rgba(0,0,0,0)')
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_bar:
    fig_bar = px.bar(
        orbit_counts, x='orbit_type', y='count', color='type',
        title='Active Satellites vs Debris by Orbit',
        color_discrete_map=type_colors,
        labels={'orbit_type': 'Orbit', 'count': 'Objects', 'type': 'Type'},
        barmode='group'
    )
    fig_bar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color=MOCHA['text'], title_font_color=MOCHA['mauve'],
        legend=dict(bgcolor='rgba(0,0,0,0)'),
        xaxis=dict(gridcolor=MOCHA['overlay']),
        yaxis=dict(gridcolor=MOCHA['overlay'])
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()


# ── Top 10 Countries ──────────────────────────────────────────────────────────
st.markdown(f"""
<div class="card">
    <div class="section-title">🌐 Top 10 Countries by Objects in Orbit</div>
    <div class="section-desc">Which nations are responsible for the most tracked orbital objects — active or debris.</div>
</div>
""", unsafe_allow_html=True)

country_counts = (
    filtered.groupby(['COUNTRY_CODE', 'type'])
    .size().reset_index(name='count')
)
top_countries = (
    country_counts.groupby('COUNTRY_CODE')['count']
    .sum().nlargest(10).index
)
top_df = country_counts[country_counts['COUNTRY_CODE'].isin(top_countries)]

fig_countries = px.bar(
    top_df, x='COUNTRY_CODE', y='count', color='type',
    title='Top 10 Countries — Active Satellites vs Debris',
    color_discrete_map=type_colors,
    labels={'COUNTRY_CODE': 'Country', 'count': 'Objects', 'type': 'Type'},
    barmode='stack'
)
fig_countries.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font_color=MOCHA['text'], title_font_color=MOCHA['mauve'],
    legend=dict(bgcolor='rgba(0,0,0,0)'),
    xaxis=dict(gridcolor=MOCHA['overlay']),
    yaxis=dict(gridcolor=MOCHA['overlay'])
)
st.plotly_chart(fig_countries, use_container_width=True)

st.divider()


# ── Timeline ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="card">
    <div class="section-title">📈 Orbital Growth Over Time</div>
    <div class="section-desc">Cumulative number of objects added to orbit each year. The steep rise after 2019 reflects the Starlink mega-constellation era.</div>
</div>
""", unsafe_allow_html=True)

if 'launch_year' in filtered.columns:
    timeline_df = (
        filtered.dropna(subset=['launch_year'])
        .groupby(['launch_year', 'type'])
        .size().reset_index(name='count')
    )
    timeline_df = timeline_df[
        (timeline_df['launch_year'] >= 1957) &
        (timeline_df['launch_year'] <= 2025)
    ]
    timeline_df = timeline_df.sort_values('launch_year')
    timeline_df['cumulative'] = timeline_df.groupby('type')['count'].cumsum()

    fig_time = px.line(
        timeline_df, x='launch_year', y='cumulative', color='type',
        title='Cumulative Objects in Orbit by Launch Year',
        color_discrete_map=type_colors,
        labels={'launch_year': 'Year', 'cumulative': 'Cumulative Objects', 'type': 'Type'},
        markers=False
    )
    fig_time.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color=MOCHA['text'], title_font_color=MOCHA['mauve'],
        legend=dict(bgcolor='rgba(0,0,0,0)'),
        xaxis=dict(gridcolor=MOCHA['overlay']),
        yaxis=dict(gridcolor=MOCHA['overlay'])
    )
    st.plotly_chart(fig_time, use_container_width=True)
else:
    st.info("Launch year data not available in current dataset.")

st.divider()


# ── Satellite Search ──────────────────────────────────────────────────────────
st.markdown(f"""
<div class="card">
    <div class="section-title">🔍 Satellite Search</div>
    <div class="section-desc">Search for any tracked object by name. Try: STARLINK, ISS, NOAA, COSMOS.</div>
</div>
""", unsafe_allow_html=True)

search = st.text_input("Object name:", placeholder="e.g. ISS, STARLINK, NOAA...")
if search:
    matches = all_objects[all_objects['OBJECT_NAME'].str.contains(search.upper(), na=False)]
    if not matches.empty:
        st.success(f"Found {len(matches):,} object(s) matching **{search.upper()}**")
        display_cols = [c for c in ['OBJECT_NAME', 'NORAD_CAT_ID', 'COUNTRY_CODE', 'orbit_type', 'EPOCH', 'type']
                       if c in matches.columns]
        st.dataframe(
            matches[display_cols].head(50),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning(f"No objects found matching **{search.upper()}**")

st.divider()


# ── Debris Inventory ──────────────────────────────────────────────────────────
st.markdown(f"""
<div class="card">
    <div class="section-title">🗂️ Debris Inventory</div>
    <div class="section-desc">Searchable, sortable table of tracked debris objects. Click column headers to sort.</div>
</div>
""", unsafe_allow_html=True)

if st.checkbox("Show debris inventory"):
    display_debris_cols = [c for c in ['OBJECT_NAME', 'NORAD_CAT_ID', 'COUNTRY_CODE', 'orbit_type', 'EPOCH']
                          if c in debris_sats.columns]
    debris_display = debris_sats[display_debris_cols].copy()
    debris_display['orbit_type'] = debris_sats['MEAN_MOTION'].apply(classify_orbit)

    search_debris = st.text_input("Search within inventory:", placeholder="Filter by name or country...")
    if search_debris:
        mask = debris_display.apply(
            lambda row: row.astype(str).str.contains(search_debris.upper(), case=False).any(),
            axis=1
        )
        debris_display = debris_display[mask]

    st.caption(f"Showing {min(500, len(debris_display)):,} of {len(debris_display):,} objects")
    st.dataframe(debris_display.head(500), use_container_width=True, hide_index=True)


# ── Risk Index ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="card">
    <div class="section-title">⚠️ Orbital Congestion Risk Index</div>
    <div class="section-desc">
        Satellites sharing the same orbital band and inclination as high debris density 
        face greater collision risk. This index groups objects into orbital bins and 
        calculates the debris-to-total ratio per band — a relative risk proxy.
        <br><br>
        <b>This is not a conjunction prediction</b> — it's a statistical density analysis 
        based on orbital parameters.
    </div>
</div>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def compute_risk(active_df, debris_df):
    # Crear bins de altitud usando MEAN_MOTION (proxy de altitud)
    # y bins de inclinación — define el "carril orbital"
    combined = pd.concat([active_df, debris_df], ignore_index=True)
    
    combined['motion_bin'] = pd.cut(
        combined['MEAN_MOTION'],
        bins=50,  # 50 bandas orbitales
        labels=False
    )
    combined['incl_bin'] = pd.cut(
        combined['INCLINATION'],
        bins=18,  # bins de 10 grados cada uno (0-180°)
        labels=False
    )
    
    # Contar objetos por bin
    bin_counts = combined.groupby(['motion_bin', 'incl_bin']).agg(
        total=('type', 'count'),
        debris_count=('type', lambda x: (x == 'debris').sum())
    ).reset_index()
    
    bin_counts['debris_ratio'] = bin_counts['debris_count'] / bin_counts['total']
    
    # Asignar score a cada satélite activo
    active_scored = active_df.copy()
    active_scored['motion_bin'] = pd.cut(
        active_scored['MEAN_MOTION'], bins=50, labels=False
    )
    active_scored['incl_bin'] = pd.cut(
        active_scored['INCLINATION'], bins=18, labels=False
    )
    
    active_scored = active_scored.merge(
        bin_counts[['motion_bin', 'incl_bin', 'debris_ratio', 'debris_count', 'total']],
        on=['motion_bin', 'incl_bin'],
        how='left'
    )
    
    # Normalizar score 0-100
    max_ratio = active_scored['debris_ratio'].max()
    active_scored['risk_score'] = (
        (active_scored['debris_ratio'] / max_ratio) * 100
    ).round(1)
    
    return active_scored, bin_counts
active_sats['orbit_type'] = active_sats['MEAN_MOTION'].apply(classify_orbit)
active_scored, bin_counts = compute_risk(active_sats, debris_sats)


# ── Heatmap de densidad ───────────────────────────────────────────────────────
st.markdown(f"<h4 style='color:{MOCHA['mauve']};'>🗺️ Orbital Density Heatmap</h4>", unsafe_allow_html=True)
st.caption("Each cell = one orbital band × inclination zone. Color = debris density ratio.")

fig_heat = px.density_heatmap(
    active_scored,
    x='INCLINATION',
    y='MEAN_MOTION',
    z='risk_score',
    nbinsx=36,
    nbinsy=50,
    color_continuous_scale=[
        [0.0,  MOCHA['surface']],
        [0.3,  MOCHA['teal']],
        [0.6,  MOCHA['peach']],
        [1.0,  MOCHA['pink']],
    ],
    labels={
        'INCLINATION': 'Inclination (degrees)',
        'MEAN_MOTION': 'Mean Motion (rev/day) → Altitude proxy',
        'risk_score': 'Risk Score'
    },
    title='Debris Density by Orbital Band and Inclination'
)
fig_heat.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color=MOCHA['text'],
    title_font_color=MOCHA['mauve'],
    yaxis=dict(autorange='reversed', gridcolor=MOCHA['overlay']),
    xaxis=dict(gridcolor=MOCHA['overlay'])
)
st.plotly_chart(fig_heat, use_container_width=True)

# ── Top 20 satélites en mayor riesgo ─────────────────────────────────────────
st.markdown(f"<h4 style='color:{MOCHA['mauve']};'>🚨 Top 20 Most Exposed Satellites</h4>", unsafe_allow_html=True)
st.caption("Active satellites in the most debris-congested orbital bands.")

top_risk = (
    active_scored[['OBJECT_NAME', 'NORAD_CAT_ID', 'COUNTRY_CODE', 
                   'orbit_type', 'risk_score', 'debris_count', 'total']]
    .dropna(subset=['risk_score'])
    .sort_values('risk_score', ascending=False)
    .head(20)
    .rename(columns={
        'risk_score':    'Risk Score (0-100)',
        'debris_count':  'Debris in Band',
        'total':         'Total Objects in Band'
    })
)

fig_risk = px.bar(
    top_risk,
    x='Risk Score (0-100)',
    y='OBJECT_NAME',
    orientation='h',
    color='Risk Score (0-100)',
    color_continuous_scale=[
        [0.0, MOCHA['teal']],
        [0.5, MOCHA['peach']],
        [1.0, MOCHA['pink']],
    ],
    title='Top 20 Active Satellites by Congestion Risk Score',
    labels={'OBJECT_NAME': ''}
)
fig_risk.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color=MOCHA['text'],
    title_font_color=MOCHA['mauve'],
    yaxis=dict(autorange='reversed', gridcolor=MOCHA['overlay']),
    xaxis=dict(gridcolor=MOCHA['overlay']),
    coloraxis_showscale=False
)
st.plotly_chart(fig_risk, use_container_width=True)

# Tabla detallada
with st.expander("📋 View full risk table"):
    st.dataframe(
        active_scored[['OBJECT_NAME', 'NORAD_CAT_ID', 'COUNTRY_CODE',
                       'orbit_type', 'risk_score', 'debris_count']]
        .dropna(subset=['risk_score'])
        .sort_values('risk_score', ascending=False)
        .rename(columns={'risk_score': 'Risk Score', 'debris_count': 'Debris in Band'})
        .reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(f"""
<div style='text-align:center; color:{MOCHA["subtext"]}; font-size:0.8rem; padding:12px 0;'>
    Data source: <a href='https://www.space-track.org' style='color:{MOCHA["mauve"]};'>Space-Track.org</a>
    · Updated weekly via GitHub Actions
    · Built with Streamlit + Plotly
</div>
""", unsafe_allow_html=True)
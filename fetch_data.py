import requests
import pandas as pd
import os
from datetime import datetime
from io import StringIO
import time

SPACETRACK_USER = os.getenv('SPACETRACK_USER')
SPACETRACK_PASS = os.getenv('SPACETRACK_PASS')

if not SPACETRACK_USER or not SPACETRACK_PASS:
    # Si no hay variables de entorno, lee del secrets local
    try:
        import tomllib
        with open('.streamlit/secrets.toml', 'rb') as f:
            secrets = tomllib.load(f)
        SPACE_TRACK_USER = secrets['SPACE_TRACK_USER']
        SPACE_TRACK_PASS = secrets['SPACE_TRACK_PASS']
    except Exception as e:
        print(f"Error leyendo credenciales: {e}")
        exit(1)

def fetch_from_spacetrack():
    session = requests.Session()

    print("Logging in to Space-Track...")
    login = session.post(
        'https://www.space-track.org/ajaxauth/login',
        data={'identity': SPACE_TRACK_USER, 'password': SPACE_TRACK_PASS},
        timeout=30
    )

    print(f"Login status: {login.status_code}")
    print(f"Login response: '{login.text}'")
    print(f"User being sent: '{SPACE_TRACK_USER}'")

    if login.status_code != 200:
        print(f"Login failed: {login.status_code}")
        return

    base = 'https://www.space-track.org/basicspacedata/query/class/gp'

    print("Downloading active satellites...")
    active_r = session.get(
        f'{base}/OBJECT_TYPE/PAYLOAD/format/csv/emptyresult/show',
        timeout=60
    )

        time.sleep(3)  # respetar rate limit

    print("Downloading debris...")
    debris_r = session.get(
        f'{base}/OBJECT_TYPE/DEBRIS/format/csv/emptyresult/show',
        timeout=60
    )

    session.get('https://www.space-track.org/ajaxauth/logout')

    # Guardar CSVs
    active_df = pd.read_csv(StringIO(active_r.text))
    debris_df = pd.read_csv(StringIO(debris_r.text))

    os.makedirs('data', exist_ok=True)
    active_df.to_csv('data/active_satellites.csv', index=False)
    debris_df.to_csv('data/debris.csv', index=False)

    # Guardar metadata — fecha de última actualización
    with open('data/last_updated.txt', 'w') as f:
        f.write(datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M UTC'))

    print(f"Done. Active: {len(active_df)} | Debris: {len(debris_df)}")
    print(f"Files saved to /data")

if __name__ == '__main__':
    fetch_from_spacetrack()
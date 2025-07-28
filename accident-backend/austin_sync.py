import pandas as pd
import requests
import sqlite3
from datetime import datetime

# City configurations
city_sources = {
    "Austin": {
        "url": "https://data.austintexas.gov/resource/y2wy-tgr5.json",
        "date_field": "crash_timestamp",
        "id_field": "cris_crash_id",
        "use_where": True,
        "state": "TX"
    },
    }


db_path = "accidents.db"
log_table = "etl_logs"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute(f"CREATE TABLE IF NOT EXISTS {log_table} (run_time TEXT, city TEXT, state TEXT, source TEXT, inserted_rows INTEGER)")
conn.commit()

def clean_and_insert(df, city, source_url, state):
    if df.empty:
        return

    df['city'] = city
    df['state'] = state
    df['country'] = 'US'
    df['end_time'] = df.get('start_time', pd.NaT)
    df['end_lat'] = df.get('start_lat', pd.NA)
    df['end_lng'] = df.get('start_lng', pd.NA)
    df['distance(mi)'] = 0.1
    df['timezone'] = 'US/Eastern'
    df['description'] = 'Auto-Crash'
    if 'severity' not in df.columns:
        df['severity'] = 2
    else:
        df['severity'] = pd.to_numeric(df['severity'], errors='coerce').fillna(2).astype(int)

    df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
    df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce')
    df = df[df['start_time'].dt.year >= 2024]

    columns_to_use = [
        'id', 'start_time', 'end_time', 'start_lat', 'start_lng', 'end_lat', 'end_lng',
        'distance(mi)', 'description', 'street', 'city', 'state', 'country', 'timezone', 'severity'
    ]
    for col in columns_to_use:
        if col not in df.columns:
            df[col] = pd.NA

    df = df[columns_to_use].dropna(subset=['id', 'start_time'])
    df = df.loc[:, ~df.columns.duplicated()]

    existing_ids = pd.read_sql(f"SELECT DISTINCT id FROM accidents WHERE city=?", conn, params=(city,))['id'].tolist()
    new_df = df[~df['id'].isin(existing_ids)]
    rows_inserted = len(new_df)
    if rows_inserted > 0:
        new_df.to_sql("accidents", conn, if_exists='append', index=False)

    cursor.execute(f"INSERT INTO {log_table} (run_time, city, state, source, inserted_rows) VALUES (?, ?, ?, ?, ?)",
                   (datetime.now().isoformat(), city, state, source_url, rows_inserted))
    conn.commit()
    print(f"✅ {city}: {rows_inserted} rows inserted.")

for city, config in city_sources.items():
    url = config["url"]
    date_field = config["date_field"]
    id_field = config["id_field"]
    use_where = config.get("use_where", True)
    state = config.get("state", "NA")

    print(f"🔄 Starting paginated fetch for {city}...")
    for offset in range(0, 100000, 1000):
        params = {
            "$limit": 1000,
            "$offset": offset,
            "$order": f"{date_field} DESC"
        }
        if use_where:
            params["$where"] = f"{date_field} >= '2024-01-01T00:00:00' AND {date_field} < '2025-01-01T00:00:00'"

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"⚠️ API error at offset {offset}: {response.status_code}")
                break
            batch = response.json()
            if not batch:
                print(f"✅ {city}: No more data at offset {offset}")
                break
            df = pd.DataFrame(batch)
            print(f"✔️ Retrieved {len(df)} rows at offset {offset} for {city}")
            if date_field in df.columns:
                df['start_time'] = df[date_field]
            if id_field in df.columns:
                df['id'] = df[id_field]
            elif 'id' not in df.columns:
                df['id'] = df.index.astype(str)
            if 'latitude' in df.columns:
                df['start_lat'] = df['latitude']
            if 'longitude' in df.columns:
                df['start_lng'] = df['longitude']
            if 'location' in df.columns and isinstance(df['location'].iloc[0], dict):
                df['start_lat'] = df['location'].apply(lambda x: x.get('lat') if isinstance(x, dict) else None)
                df['start_lng'] = df['location'].apply(lambda x: x.get('lon') if isinstance(x, dict) else None)
            if 'street_name' in df.columns:
                df['street'] = df['street_name']
            elif 'on_street_name' in df.columns:
                df['street'] = df['on_street_name']
            clean_and_insert(df, city, url, state)
            print(f"➡️ {city}: Offset {offset} processed.")
        except Exception as e:
            print(f"❌ Error fetching {city} at offset {offset}: {e}")
            break

conn.close()

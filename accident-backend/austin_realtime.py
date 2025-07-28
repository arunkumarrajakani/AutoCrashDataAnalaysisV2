
import pandas as pd
import requests
import sqlite3
from datetime import datetime

# SQLite DB path
db_path = "accidents.db"
log_table = "etl_logs"
api_url = "https://data.austintexas.gov/resource/y2wy-tgr5.json"

# Aggregate results
all_data = []
batch_size = 1000
max_pages = 5  # fetch up to 5000 records
for offset in range(0, batch_size * max_pages, batch_size):
    params = {
        "$order": "crash_timestamp DESC",
        "$limit": batch_size,
        "$offset": offset
    }
    resp = requests.get(api_url, params=params)
    if resp.status_code != 200:
        print(f"⚠️ API error at offset {offset}")
        break
    batch = resp.json()
    if not batch:
        break
    all_data.extend(batch)

# Convert to DataFrame
df = pd.DataFrame(all_data)
print("Columns from API:", df.columns.tolist())

# Drop redundant 'id' column if both 'id' and 'cris_crash_id' exist
if 'id' in df.columns and 'cris_crash_id' in df.columns:
    df = df.drop(columns=['id'])

# Rename columns
df = df.rename(columns={
    'cris_crash_id': 'id',
    'latitude': 'start_lat',
    'longitude': 'start_lng',
    'rpt_street_name': 'street',
    'crash_sev_id': 'severity'
})

# Assign time
if 'crash_timestamp' in df.columns:
    df['start_time'] = df['crash_timestamp']
elif 'crash_timestamp_ct' in df.columns:
    df['start_time'] = df['crash_timestamp_ct']
else:
    df['start_time'] = pd.NaT

# Add required/default columns
df['state'] = 'TX'
df['city'] = 'Austin'
df['country'] = 'US'
df['end_time'] = df['start_time']
df['end_lat'] = df['start_lat']
df['end_lng'] = df['start_lng']
df['distance(mi)'] = 0.1
df['timezone'] = 'US/Central'
df['description'] = 'Auto-Crash'
df['severity'] = pd.to_numeric(df['severity'], errors='coerce').fillna(2).astype(int)

# Convert timestamps
df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce')

# Filter 2025+ data
df = df[df['start_time'].dt.year >= 2024]

# Ensure schema
columns_to_use = [
    'id', 'start_time', 'end_time', 'start_lat', 'start_lng', 'end_lat', 'end_lng',
    'distance(mi)', 'description', 'street', 'city', 'state', 'country', 'timezone', 'severity'
]
for col in columns_to_use:
    if col not in df.columns:
        df[col] = pd.NA
df = df[columns_to_use].dropna(subset=['id', 'start_time'])
df = df.loc[:, ~df.columns.duplicated()]

# Connect DB
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute(f"CREATE TABLE IF NOT EXISTS {log_table} (run_time TEXT, source TEXT, inserted_rows INTEGER)")
conn.commit()

# De-duplicate
existing_ids_df = pd.read_sql("SELECT DISTINCT id FROM accidents WHERE city='Austin'", conn)
existing_ids = existing_ids_df['id'].drop_duplicates().tolist()
new_df = df[~df['id'].isin(existing_ids)]

# Insert
rows_inserted = len(new_df)
if rows_inserted > 0:
    new_df.to_sql('accidents', conn, if_exists='append', index=False)

cursor.execute(f"INSERT INTO {log_table} (run_time, source, inserted_rows) VALUES (?, ?, ?)",
               (datetime.now().isoformat(), api_url, rows_inserted))

conn.commit()
conn.close()
print(f"✅ {rows_inserted} new records inserted and logged.")

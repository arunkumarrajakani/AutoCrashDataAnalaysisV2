import pandas as pd
from sqlalchemy import create_engine

print("Reading CSV...")
df = pd.read_csv("cleaned_crash_data.csv")

print("Connecting to DB...")
engine = create_engine('sqlite:///accidents.db')

# Break into chunks
chunksize = 100_000
total_rows = 0

print("Writing to DB in chunks...")
for i, chunk in enumerate(pd.read_csv("cleaned_crash_data.csv", chunksize=chunksize)):
    chunk.to_sql('accidents', con=engine, if_exists='append', index=False)
    total_rows += len(chunk)
    print(f"✅ Loaded {total_rows} rows so far...")

print("🎉 Done. All data written.")

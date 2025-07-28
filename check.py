import sqlite3
conn = sqlite3.connect('accidents.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM accidents")
print("Total rows inserted so far:", cursor.fetchone()[0])
conn.close()

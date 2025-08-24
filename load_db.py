import sqlite3

con = sqlite3.connect('pharmacy.db')
cur = con.cursor()
with open('schema.sql') as f:
    cur.executescript(f.read())
con.commit()
print("Database created: pharmacy.db")


import sqlite3

# CONNECTION SETUP
con = sqlite3.connect("../riaadb.db")

cur = con.cursor()

cur.execute("SELECT riaa.ID, riaa_hist.CERT_DATE, riaa.CERT_TYPE, * FROM riaa JOIN riaa_hist ON ID = RIAAID WHERE riaa_hist.CERT_DATE LIKE '____-%-%';")
rows = cur.fetchall()

years = {}

for row in rows:
    year = row[1].split("-")[0]

    if not year in years:
        years[year] = {
            'total': 0,
            'ST': 0,
            'LA': 0,
            'DI': 0,
            'MT': 0
        }
    
    years[year]['total'] += 1
    years[year][row[2]] += 1

keys = list(years.keys())
keys.sort()

print("YEAR,TOTAL,ST,DI,LA,MT")
for key in keys:
    print(f"{key},{years[key]['total']},{years[key]['ST']},{years[key]['DI']},{years[key]['LA']},{years[key]['MT']}")

cur.close()
con.close()
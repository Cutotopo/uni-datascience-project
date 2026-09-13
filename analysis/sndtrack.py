import sqlite3

# CONNECTION SETUP
con = sqlite3.connect("../riaadb.db")

cur = con.cursor()

cur.execute("SELECT riaa.ID, riaa.ARTIST, riaa_meta.RELEASE_DATE, riaa_meta.CERT_DATE_FIRST, riaa_meta.GENRE FROM riaa JOIN riaa_meta ON ID = RIAAID WHERE riaa_meta.RELEASE_DATE LIKE '____-%-%' AND riaa_meta.RELEASE_DATE <> '0000-00-00' AND riaa_meta.CERT_DATE_FIRST LIKE '____-%-%' AND riaa_meta.CERT_DATE_FIRST <> '0000-00-00' AND (riaa.ARTIST = 'SOUNDTRACK' OR riaa_meta.GENRE = 'SOUNDTRACK');")
rows = cur.fetchall()

years = {}

for row in rows:
    ryear = row[2].split("-")[0]
    cyear = row[3].split("-")[0]

    if not ryear in years:
        years[ryear] = {
            'certs': 0,
            'releases': 0
        }
    
    if not cyear in years:
        years[cyear] = {
            'certs': 0,
            'releases': 0
        }
    
    years[ryear]['releases'] += 1
    years[cyear]['certs'] += 1

keys = list(years.keys())
keys.sort()

print("YEAR,RELEASES,CERTS")
for key in keys:
    print(f"{key},{years[key]['releases']},{years[key]['certs']}")

cur.close()
con.close()
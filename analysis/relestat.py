from datetime import date
import sqlite3

# CONNECTION SETUP
con = sqlite3.connect("../riaadb.db")

cur = con.cursor()

cur.execute("SELECT RELEASE_TYPE, RELEASE_DATE, CERT_DATE_FIRST, CERT_TYPE FROM riaa_meta JOIN riaa ON ID = RIAAID WHERE RELEASE_DATE LIKE '____-%-%' AND CERT_DATE_FIRST LIKE '____-%-%' AND RELEASE_DATE <> '0000-00-00'")
rows = cur.fetchall()

pcnt = 0
pobj = {}

for row in rows:
    releasedate = row[1].split("-")
    certdate = row[2].split("-")

    reldt = date(int(releasedate[0]), int(releasedate[1]), int(releasedate[2]))
    crtdt = date(int(certdate[0]), int(certdate[1]), int(certdate[2]))

    if crtdt >= reldt:
        pcnt += 1

        delta = crtdt - reldt

        if not f"{releasedate[0]}" in pobj:
            pobj[f"{releasedate[0]}"] = {
                'total': [],
                'types': {
                    'ST': [],
                    'DI': [],
                    'LA': [],
                    'MT': []
                }
            }
        
        pobj[f"{releasedate[0]}"]['total'].append(delta.days)
        pobj[f"{releasedate[0]}"]['types'][row[3]].append(delta.days)

# print(f"valid release/cert relationships: {pcnt}/{len(rows)}")

keys = list(pobj.keys())
keys.sort()

print("YEAR,DAYS,ST,DI,LA,MT")
for key in keys:
    val = pobj[key]['total']
    val.sort()
    val = val[len(val) // 2] if len(val) else ''

    st = pobj[key]['types']['ST']
    st.sort()
    st = st[len(st) // 2] if len(st) else ''

    di = pobj[key]['types']['DI']
    di.sort()
    di = di[len(di) // 2] if len(di) else ''

    la = pobj[key]['types']['LA']
    la.sort()
    la = la[len(la) // 2] if len(la) else ''

    mt = pobj[key]['types']['MT']
    mt.sort()
    mt = mt[len(mt) // 2] if len(mt) else ''

    print(f"{key},{val},{st},{di},{la},{mt}")

cur.close()
con.close()

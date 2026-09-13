import colorama
from functools import reduce
import json
import requests
import sqlite3
import sys
import time

botua = "cutoosc/1.0 (+me@cutotopo.live)"
headers = {"User-Agent": botua}

def mb_get_artist(ambid):
    print(f"mb_get_artist: {colorama.Fore.CYAN}fetching mbid {ambid}.{colorama.Fore.RESET}", file=sys.stderr)
    ok = False
    while not ok:
        time.sleep(1.5)
        try:
            res = requests.get(f"https://musicbrainz.org/ws/2/artist/{ambid}?fmt=json", headers=headers)
            ok = res.ok

            if not ok:
                print(f"mb_get_artist: {colorama.Fore.YELLOW}warn: server returned a non-ok status code. trying again in 1.5 seconds.{colorama.Fore.RESET}", file=sys.stderr)
        except requests.exceptions.ConnectionError:
            ok = False
            print(f"mb_get_artist: {colorama.Fore.YELLOW}warn: requests crashed due to a connection error. trying again in 1.5 seconds.{colorama.Fore.RESET}", file=sys.stderr)
    return res.content

def encode_csv(str):
    str = str.replace("\n", "")
    quoted = False
    if ',' in str:
        quoted = True
    if '"' in str:
        quoted = True
        str = str.replace("\"", "\"\"")
    if quoted:
        return f"\"{str}\""
    return str

# CONNECTION SETUP
con = sqlite3.connect("../riaadb.db")
cur = con.cursor()

cur.execute("SELECT ARTIST, MBResponse, CERT_LEVEL, RELEASE_TYPE, CERT_TYPE, CERT_GOLD, CERT_PLATINUM, CERT_DIAMOND FROM riaa JOIN musicbrainz_raw ON RIAAID = ID WHERE MatchFailure = 0 AND MatchTier IN (1, 2)")
rows = cur.fetchall()

types = ["ST", "DI", "LA"]

artists = {}

for row in rows:
    artistname = row[0]
    mbresponse = json.loads(row[1])

    mbkey = 'recordings' if 'recordings' in mbresponse else 'release-groups'

    mtc = mbresponse[mbkey][0]
    
    for (aidx, artist) in enumerate(mtc['artist-credit']):
        ambid = artist['artist']['id']

        if artist['artist']['name'] == 'Various Artists':
            continue

        if ambid not in artists:
            cur.execute("SELECT * FROM musicbrainz_artist_cache WHERE MBID = ?", (ambid,))
            dbres = cur.fetchmany()
            if not len(dbres):
                cnt = mb_get_artist(ambid)
                with con:
                    cur.execute("INSERT INTO musicbrainz_artist_cache (MBID, MBResponse) VALUES (?, ?);", (ambid, cnt))
            else:
                print(f"mb_get_area: {colorama.Fore.CYAN}info: mbid {ambid} was already cached.{colorama.Fore.RESET}", file=sys.stderr)
                cnt = dbres[0][1]
            
            cnt = json.loads(cnt)
            area = "XW"
            try:
                area = cnt['area']['iso-3166-1-codes'][0]
            except:
                pass

            artists[ambid] = {
                'name': artist['artist']['name'],
                'totals': { # total nominations
                    'lead': 0,
                    'featuring': 0
                },
                'country': area,
                'awards': {},
                'totalscore': 0
            }
        
        artistdata = artists[ambid]

        artistdata['totalscore'] += row[2]

        if aidx == 0: # lead artist
            artistdata['totals']['lead'] += 1

            if row[4] not in artistdata['awards']:
                artistdata['awards'][row[4]] = {
                    'gold': 0,
                    'platinum': 0,
                    'diamond': 0,
                    'score': 0
                }
            
            artistdata['awards'][row[4]]['gold'] += row[5]
            artistdata['awards'][row[4]]['platinum'] += row[6]
            artistdata['awards'][row[4]]['diamond'] += row[7]
            artistdata['awards'][row[4]]['score'] += row[2]
            continue
        else: # participating artist
            artistdata['totals']['featuring'] += 1
            continue

aridx = list(artists.keys())
aridx.sort()

score_headers = ",".join(reduce(lambda a, b: a + b, [[f"TOTAL_{i}_GOLD", f"TOTAL_{i}_PLATINUM", f"TOTAL_{i}_DIAMOND", f"TOTAL_{i}_SCORE"] for i in types]))

print(f"ARTIST_NAME,MBID,COUNTRY,AWARDS_LEAD,AWARDS_FEATURING,TOTAL_SCORE,{score_headers}")
for mbid in aridx:
    artist = artists[mbid]
    print(f"{encode_csv(artist['name'])},{mbid},{artist['country']},{artist['totals']['lead']},{artist['totals']['featuring']},{artist['totalscore']}", end="")
    for type in types:
        if type not in artist['awards']:
            print(",0,0,0,0", end="")
            continue
        gold = artist['awards'][type]['gold']
        plat = artist['awards'][type]['platinum']
        diam = artist['awards'][type]['diamond']
        scor = artist['awards'][type]['score']
        print(f",{gold},{plat},{diam},{scor}", end="")
    print("")

cur.close()
con.close()
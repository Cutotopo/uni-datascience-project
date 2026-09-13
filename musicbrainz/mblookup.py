import colorama
from functools import reduce
import json
import requests
import sqlite3
import sys
import time

botua = "cutoosc/1.0 (+me@cutotopo.live)"
headers = {"User-Agent": botua}

def mb_lookup(dmbid, engine):
    print(f"mb_lookup: {colorama.Fore.CYAN}fetching mbid {dmbid}.{colorama.Fore.RESET}", file=sys.stderr)

    if engine == 'recording':
        inc = 'genres+releases+release-groups'
    else:
        inc = 'genres+releases'

    ok = False
    while not ok:
        time.sleep(1.5)
        try:
            res = requests.get(f"https://musicbrainz.org/ws/2/{engine}/{dmbid}?inc={inc}&fmt=json", headers=headers)
            ok = res.ok

            if not ok:
                print(f"mb_lookup: {colorama.Fore.YELLOW}warn: server returned a non-ok status code. trying again in 1.5 seconds.{colorama.Fore.RESET}", file=sys.stderr)
        except requests.exceptions.ConnectionError:
            ok = False
            print(f"mb_lookup: {colorama.Fore.YELLOW}warn: requests crashed due to a connection error. trying again in 1.5 seconds.{colorama.Fore.RESET}", file=sys.stderr)
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

cur.execute("SELECT * FROM musicbrainz_raw WHERE MatchFailure = 0 AND MatchTier IN (1, 2, 4);")
rows = cur.fetchall()
rowl = len(rows)

for (i, row) in enumerate(rows):
    print(f"main: ========== [{i + 1}/{rowl}] ==========", file=sys.stderr)
    start = time.time()

    mbresponse = json.loads(row[1])

    mbkey = 'recordings' if 'recordings' in mbresponse else 'release-groups'

    mtc = mbresponse[mbkey][0]
    mbid = mtc['id']

    print(f"main: {colorama.Fore.CYAN}got mbid: {mbid} ({mbkey}).{colorama.Fore.RESET}", file=sys.stderr)

    dbq = cur.execute("SELECT * FROM musicbrainz_lookup_cache WHERE MBID = ?;", (mbid,))
    dbr = dbq.fetchall()
    if len(dbr):
        print(f"main: {colorama.Fore.GREEN}mbid cache hit!{colorama.Fore.RESET}", file=sys.stderr)
        res = dbr[0][1]
    else:
        print(f"main: {colorama.Fore.CYAN}mbid cache miss! fetching...{colorama.Fore.RESET}", file=sys.stderr)
        res = mb_lookup(mbid, mbkey[:-1])

        with con:
            cur.execute("INSERT INTO musicbrainz_lookup_cache (MBID, MBResponse) VALUES (?, ?)", (mbid, res))

    print(f"main: {colorama.Fore.GREEN}got data, in {"{:.2f}".format(time.time() - start)}s.{colorama.Fore.RESET}", file=sys.stderr)
    

cur.close()
con.close()
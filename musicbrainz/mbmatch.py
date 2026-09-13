import colorama
import json
import requests
import sqlite3
import time
import sys

botua = "cutoosc/1.0 (+me@cutotopo.live)"
headers = {"User-Agent": botua}

RELTYPE_TEMPLATE = {
    'SINGLE': {
        'type': 'recording',
        'queries': [
            'artist:"%%ARTIST%%" AND recording:"%%TITLE%%"',
            'artist:"%%ARTIST%%" AND recording:(%%TITLE%%)',
            'artist:(%%ARTIST%%) AND recording:(%%TITLE%%)',
            'recording:(%%TITLE%%) AND secondarytype:soundtrack'
        ]
    },
    'ALBUM': {
        'type': 'release-group',
        'queries': [
            'artist:"%%ARTIST%%" AND releasegroup:"%%TITLE%%"',
            'artist:"%%ARTIST%%" AND releasegroup:(%%TITLE%%)',
            'artist:(%%ARTIST%%) AND releasegroup:(%%TITLE%%)',
            'releasegroup:(%%TITLE%%) AND secondarytype:soundtrack'
        ]
    },
    'VIDEO LONGFORM': {
        'type': 'recording',
        'queries': [
            'artist:"%%ARTIST%%" AND recording:"%%TITLE%%"',
            'artist:"%%ARTIST%%" AND recording:(%%TITLE%%)',
            'artist:(%%ARTIST%%) AND recording:(%%TITLE%%)',
            'recording:(%%TITLE%%) AND secondarytype:soundtrack'
        ]
    },
    'VIDEO SINGLE': {
        'type': 'recording',
        'queries': [
            'artist:"%%ARTIST%%" AND recording:"%%TITLE%%"',
            'artist:"%%ARTIST%%" AND recording:(%%TITLE%%)',
            'artist:(%%ARTIST%%) AND recording:(%%TITLE%%)',
            'recording:(%%TITLE%%) AND secondarytype:soundtrack'
        ]
    },
    'SHORT FORM ALBUM': {
        'type': 'release-group',
        'queries': [
            'artist:"%%ARTIST%%" AND releasegroup:"%%TITLE%%"',
            'artist:"%%ARTIST%%" AND releasegroup:(%%TITLE%%)',
            'artist:(%%ARTIST%%) AND releasegroup:(%%TITLE%%)',
            'releasegroup:(%%TITLE%%) AND secondarytype:soundtrack'
        ]
    },
    'VIDEO BOXSET': {
        'type': 'release-group',
        'queries': [
            'artist:"%%ARTIST%%" AND releasegroup:"%%TITLE%%"',
            'artist:"%%ARTIST%%" AND releasegroup:(%%TITLE%%)',
            'artist:(%%ARTIST%%) AND releasegroup:(%%TITLE%%)',
            'releasegroup:(%%TITLE%%) AND secondarytype:soundtrack'
        ]
    },
    'None': {
        'type': 'recording',
        'queries': [
            'artist:"%%ARTIST%%" AND recording:"%%TITLE%%"',
            'artist:"%%ARTIST%%" AND recording:(%%TITLE%%)',
            'artist:(%%ARTIST%%) AND recording:(%%TITLE%%)',
            'recording:(%%TITLE%%) AND secondarytype:soundtrack'
        ]
    },
}

# CONNECTION SETUP
con = sqlite3.connect("../riaadb.db")
con.execute("PRAGMA journal_mode=WAL;")
con.execute("PRAGMA synchronous=NORMAL;")

cur = con.cursor()

def get_mb_query_url(template, artist: str, title: str, matchtier: int = 0):
    query = template['queries'][matchtier].replace("%%ARTIST%%", mb_escape_chars_for_lucene(artist)).replace("%%TITLE%%", mb_escape_chars_for_lucene(title))
    print(f"get_mb_query_url: {colorama.Fore.CYAN}Forcing engine: {template['type']}{colorama.Fore.RESET}")
    print(f"get_mb_query_url: {colorama.Fore.GREEN}Prepared Lucene query: {query}{colorama.Fore.RESET}")
    uri = f"https://musicbrainz.org/ws/2/{template['type']}"
    return uri, query

def mb_escape_chars_for_lucene(string: str):
    spc = '+-&|!(){}[]^"~*?:\\/'
    esct = str.maketrans({ char: f"\\{char}" for char in spc })
    return str(string).translate(esct)

def musicbrainz_run_search_query(uri: str, query: str):
    print(f"musicbrainz_run_query: {colorama.Fore.CYAN}Requesting data...{colorama.Fore.RESET}", file=sys.stderr)

    params = {
        "query": query,
        "fmt": "json"
    }

    res = requests.get(uri, params=params, headers=headers)
    print(f"musicbrainz_run_query: {colorama.Fore.CYAN}Built URI: {res.url}{colorama.Fore.RESET}", file=sys.stderr)
    while not res.ok:
        if res.status_code in [503, 429, 502, 500, 504]:
            print(f"musicbrainz_run_query: {colorama.Fore.YELLOW}warn: Response was not ok (server error). Trying again in .5 seconds.{colorama.Fore.RESET}", file=sys.stderr)
            time.sleep(.5)
            print(f"musicbrainz_run_query: {colorama.Fore.CYAN}Requesting data...{colorama.Fore.RESET}", file=sys.stderr)
            res = requests.get(uri, params=params, headers=headers)
        else:
            print(f"musicbrainz_run_query: {colorama.Fore.RED}error: Response was not ok (client error, or other). Not retrying.{colorama.Fore.RESET}", file=sys.stderr)
            return b'{"count":0, "error":"client_error"}'
    print(f"musicbrainz_run_query: {colorama.Fore.GREEN}Got data.{colorama.Fore.RESET}", file=sys.stderr)
    return res.content

def zerocheck(content: str):
    try:
        j = json.loads(content)
        if j['count'] == 0:
            print(f"zerocheck: {colorama.Fore.YELLOW}warn: this query has yielded an empty result set{colorama.Fore.RESET}")
            return True
        else:
            print(f"zerocheck: {colorama.Fore.GREEN}this query has yielded at least 1 result. Saving...{colorama.Fore.RESET}")
            return False
    except:
        print(f"zerocheck: {colorama.Fore.YELLOW}warn: an error occurred while checking for results. marking as failed.{colorama.Fore.RESET}")
        return True

cur.execute("SELECT riaa.* FROM riaa LEFT JOIN musicbrainz_raw ON riaa.ID = musicbrainz_raw.RIAAID WHERE musicbrainz_raw.RIAAID IS NULL")
rows = cur.fetchall()
rowsl = len(rows)
zerocnt = 0
print(f"main: {colorama.Fore.CYAN}Got {rowsl} rows to lookup.{colorama.Fore.RESET}")
for (i, row) in enumerate(rows):
    rid = row[0]
    print(f"main: ========== [{i + 1}/{rowsl}] ==========")
    print(f"main: {colorama.Fore.CYAN}Starting resolution flow for RID: {rid}{colorama.Fore.RESET}")
    relt = RELTYPE_TEMPLATE[row[3]]
    artist = row[1]
    forcetier = -1
    if artist == "SOUNDTRACK":
        artist = ""
    if artist == "VARIOUS" and row[3] == "SINGLE":
        artist = ""
        forcetier = 3


    qcl = len(relt['queries'])
    is_empty = True
    for tier in range(qcl):
        if relt['queries'][tier] == '':
            continue

        if forcetier != -1 and tier != forcetier:
            print(f"main: {colorama.Fore.YELLOW}warn: forcing result tier ({forcetier}) for this RID, skipping query for tier {tier}{colorama.Fore.RESET}")
            continue

        if tier == 3:
            if artist != "":
                continue

        uri, query = get_mb_query_url(relt, artist, row[2], tier)
        res = musicbrainz_run_search_query(uri, query)

        if not zerocheck(res):
            is_empty = False
            break
        
        if tier != qcl - 1:
            print(f"main: {colorama.Fore.BLUE}Trying next query...{colorama.Fore.RESET}")
            time.sleep(1.5)

        continue
    
    if is_empty:
        zerocnt += 1
        print(f"main: {colorama.Fore.YELLOW}No matches found, and available queries exhausted. Giving up.{colorama.Fore.RESET}")

    sql = "INSERT INTO musicbrainz_raw (RIAAID, MBResponse, MatchTier, MatchFailure) VALUES (?, ?, ?, ?);"

    with con:
        cur.execute(sql, (rid, res, tier + 1, int(is_empty)))

    time.sleep(1.5)
    print(f"main: {colorama.Fore.GREEN}Completed resolution flow.{colorama.Fore.RESET}")

print(f"main: {colorama.Fore.GREEN}All done!{colorama.Fore.RESET}")
if zerocnt != 0:
    print(f"zerocheck: {colorama.Fore.YELLOW}warn: detected {zerocnt} ({zerocnt * 100 / rowsl}% of lookup queue) queries with empty result sets during this run.{colorama.Fore.RESET}")

con.commit()

cur.close()
con.close()

import json
import sqlite3
import sys

# CONNECTION SETUP
con = sqlite3.connect("../riaadb.db")

cur = con.cursor()

cur.execute("SELECT riaa.ID, musicbrainz_raw.MBResponse, riaa_meta.GENRE, riaa_meta.CERT_DATE_FIRST, riaa.CERT_TYPE, * FROM riaa JOIN riaa_meta ON riaa.ID = riaa_meta.RIAAID JOIN musicbrainz_raw ON riaa.ID = musicbrainz_raw.RIAAID WHERE riaa_meta.CERT_DATE_FIRST LIKE '____-%-%' AND musicbrainz_raw.MatchTier IN (1, 2, 4) AND musicbrainz_raw.MatchFailure = 0;")
rows = cur.fetchall()

riaa_valid_genres = ["ALTERNATIVE", "ROCK", "R&B/HIP HOP", "LATIN", "POP", "HOLIDAY", "COUNTRY", "JAZZ", "CHRISTIAN/GOSPEL", "SOUNDTRACK", "DANCE/ELECTRONIC", "AMERICANA/FOLK", "REGGAE", "INSTRUMENTAL", "WORLD MUSIC", "CHILDRENS", "COMEDY", "CLASSICAL", "BLUES", "OTHER"]
# "alternative" and "soundtrack" aren't technically genres in the musicbrainz database but we care about that data
riaa_musicbrainz_mappings = ["alternative", "rock", "hip hop", "latin", "pop", "christmas music", "country", "jazz", "church music", "soundtrack", "electronic", "folk", "reggae", "instrumental", "other", "children's music", "comedy", "classical", "blues", "other"]

cur.execute("SELECT a.MBID, b.GENRE_NAME FROM musicbrainz_genre AS a JOIN musicbrainz_genre AS b ON a.TOP_LEVEL_GENRE = b.ID")
genres = cur.fetchall()

genrelst = {}

for genre in genres:
    genrelst[genre[0]] = genre[1]


matchgenres = []
years = {}

for row in rows:
    riaag = row[2]
    year = row[3].split("-")[0]

    if year not in years:
        years[year] = {}
    
    genreocc = years[year]

    mbresponse = json.loads(row[1])
    mbkey = 'recordings' if 'recordings' in mbresponse else 'release-groups'

    mtc = mbresponse[mbkey][0]
    mbid = mtc['id']

    cur.execute("SELECT MBResponse FROM musicbrainz_lookup_cache WHERE MBID = ?;", (mbid,))
    res = cur.fetchmany(1)

    mtl = json.loads(res[0][0])
    genres = mtl['genres']

    if genres:
        print("genremap_musicbrainz: debug: using genre data from musicbrainz.", file=sys.stderr)
        for genre in genres:
            id = genre['id']
            toplevel = genrelst[id]

            if toplevel not in genreocc:
                genreocc[toplevel] = 0
            
            if toplevel not in matchgenres:
                matchgenres.append(toplevel)
            
            genreocc[toplevel] += 1
    elif riaag != 'None':
        print("genremap_riaa: debug: no musicbrainz genre data. using riaa data as fallback.", file=sys.stderr)
        if riaag in riaa_valid_genres:
            toplevel = riaa_musicbrainz_mappings[riaa_valid_genres.index(riaag)]
            if toplevel != "":
                if toplevel not in genreocc:
                    genreocc[toplevel] = 0
                
                if toplevel not in matchgenres:
                    matchgenres.append(toplevel)
                
                genreocc[toplevel] += 1
            else:
                print("genremap_riaa: debug: ignoring empty genre mapping record.", file=sys.stderr)
        else:
            print("genremap_riaa: warn: riaa genre record was invalid or malformed.", file=sys.stderr)
    else:
        print("main: warn: no genre data found. skipping.", file=sys.stderr)

matchgenres.sort()

print(f"YEAR,{",".join(matchgenres)}")

for year in years:
    print(year, end="")
    ydata = years[year]
    for genre in matchgenres:
        if genre not in ydata:
            print(",0", end="")
        else:
            print(f",{ydata[genre]}", end="")
    print("")


cur.close()
con.close()
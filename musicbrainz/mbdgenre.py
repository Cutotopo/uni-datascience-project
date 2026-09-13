import sqlite3
import csv

# CONNECTION SETUP
con = sqlite3.connect("../riaadb.db")
con.execute("PRAGMA journal_mode=WAL;")
con.execute("PRAGMA synchronous=NORMAL;")

cur = con.cursor()

def find_ancestor_genre(rel, gid):
    if f"{gid}" in rel:
        return int(find_ancestor_genre(rel, rel[f"{gid}"]))
    return gid

with open("datasets/l_genre_genre", "r") as f:
    links = csv.reader(f, delimiter='\t')
    parentrel = {}
    for link in links:
        if link[1] == '944810':
            if f"{link[3]}" in parentrel:
                print(f"main: warn: skipping relationship: {link[3]} -> {link[2]} as already defined for source.")
            else:
                parentrel[link[3]] = link[2]

with open("datasets/genre", "r") as f:
    genres = csv.reader(f, delimiter='\t')
    for genre in genres:
        gid = genre[0]
        ancestor = find_ancestor_genre(parentrel, gid)
        with con:
            cur.execute("INSERT INTO musicbrainz_genre (ID, MBID, GENRE_NAME, TOP_LEVEL_GENRE) VALUES (?, ?, ?, ?)", (gid, genre[1], genre[2], ancestor))

cur.close()
con.close()
CREATE TABLE musicbrainz_raw (
    RIAAID INTEGER PRIMARY KEY REFERENCES riaa(ID),
    MBResponse TEXT,
    MatchTier INTEGER,
    MatchFailure INTEGER
)
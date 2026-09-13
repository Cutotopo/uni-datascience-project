# Analysis
This module is related to processing the database contents to get them to an easily drawable form.

## Release statistics
Release statistics are built from the RIAA dataset rows that have well-formed first certification and release date values.
With all data collected as of this writing, this kind of data amounted to around 90% of the dataset. Note MusicBrainz data is not used here.

The rows matching these conditions may be quickly verified by running the following SQL query on the database:
```sql
SELECT riaa.*, RELEASE_DATE, CERT_DATE_FIRST FROM riaa_meta JOIN riaa ON ID = RIAAID WHERE RELEASE_DATE LIKE '____-%-%' AND CERT_DATE_FIRST LIKE '____-%-%' AND RELEASE_DATE <> '0000-00-00';
```

## Area statistics
Area statistics report countries by awards received.
To run this analysis, do
```bash
python3 areafreq.py > ../outputs/mbareas.csv
```

## Release statistics
Release statistics report years by awards issued to media released in that specific year.
To run this analysis, do
```bash
python3 relestat.py > ../outputs/relestat.csv
```

## Year statistics
Year statistics report years by awards issued by RIAA in a specific year.
To run this analysis, do
```bash
python3 yearcert.py > ../outputs/certstat.csv
```

## Genre statistics
Genre statistics are built from the RIAA dataset rows that have well-formed genre values.
Data is backfilled from MusicBrainz where this isn't true and data is available on there.

Genrerating genre statistics REQUIRES the `musicbrainz_raw`, `musicbrainz_lookup_cache` and `musicbrainz_genre` tables to be created and filled by the `musicbrainz` module.

To run this, do
```bash
python3 genrstat.py > ../outputs/genrtrnd.csv
```

### Soundtrack statistics
Specific statistics about soundtracks can be built from RIAA data.

```bash
python3 sndtrack.py > ../outputs/sndtrack.csv
```
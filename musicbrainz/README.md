# MusicBrainz
This module is related to MusicBrainz API scraping.

> [!IMPORTANT]
> It is assumed the `riaascrape` module has already been run.

> [!IMPORTANT]
> Please apply the SQL scripts in `./sql/` to the database before proceeding with running this module.
> They will still be marked to be applied where required but it is suggested to do this all at once before starting with this.

> [!IMPORTANT]
> Please be sure to have the packages in `../requirements.txt` available in the current Python environment.

These scripts use the SQLite database as a buffer of some sort. We store the whole responses in there so we can iterate on results from an initial large fetch without worrying about rate limits later. Responses are then processed by the scripts under `../pipeline`.

Thanks to using SQL, these scripts should be able to eventually resume in case they break or are stopped for any reason like a power outage.

## Initial scraping
Please apply `sql/mrawres.sql` to the database and then run
```bash
python3 mbmatch.py
```
to match RIAA entries to the database.

Then, apply `sql/mdacache.sql` and run
```bash
python3 mblookup.py
```
to lookup genre data for the specific scraped rows.

Then, apply `sql/midcache.sql` and run
```bash
python3 artistids.py > ../outputs/mbartist.csv
```
to generate a csv file with data about artists and their certifications.

## Genre data
Genre data requires the MusicBrainz Postgres Dump `mbdump.tar.bz2`, which can be downloaded [here](https://data.metabrainz.org/pub/musicbrainz/data/fullexport/).
Once downloaded, move the file (around 7 GiB on the 20260902 dump) to `./datasets/mbdump.tar.bz2`.
With that done, call
```bash
./genrdump.sh
```
to extract genre-related Postgres table dumps from the tarball.

With this done, apply `sql/mdagenre.sql` to the database and run
```bash
python3 mbdgenre.py
```
to populate genre relationships.

If tight on storage, the tarball can be safely deleted now.

## API notes
Unauthenticated requests have a rate limit of 1 per second (we use a 1.5s delay to be sure).

Requests should also include contact information in the user agent.

## Requests done
### Import of genre and release date
Where this data is unavailable on the RIAA database (mostly for older releases), or unreadable for other reasons (e.g. albums certified or released in the year "-0001"), data from MusicBrainz will be used.

This is done using the `mbmatch.py` script available in this directory.
Depending on the type of media, a request will be made to the MusicBrainz Lucene query engine using either the `recording` or `release-group` lookup.

Note: the database is expected to get quite big, in the order of a couple of GiB.

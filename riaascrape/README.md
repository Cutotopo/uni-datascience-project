# RIAAScrape
This module is related to RIAA website scraping.

## Fetching data
Operations should ideally be done in the following order.

First, make the output directory if not already existing
```bash
mkdir -p ../outputs
```

Then, fetch the complete certification list.
```bash
./certlist.sh
```

This has then to be processed and saved.
```bash
python3 complist.py > ../outputs/riaadata.csv
```

Now that the certification list is fully available, we can use it to get the IDs and fetch all the certification details.
```bash
./certhist.sh
```

Once that's done, we can get the available metadata from them
```bash
python3 comphist.py > ../outputs/riaahist.csv
```
```bash
python3 compmeta.py > ../outputs/riaameta.csv
```

These CSV files can now be imported in a fresh `../riaadb.db` SQLite database as-is, for later processing by the `musicbrainz` module:
 - `riaadata.csv` as `riaa`;
 - `riaahist.csv` as `riaa_history`;
 - `riaameta.csv` as `riaa_meta`.

## Expected structure
The raw RIAA AJAX requests should be stored in
 - `riaadb` for what concerns the simple page rows from the catalog
 - `riaam` for what concerns the single modal responses, that include certification history
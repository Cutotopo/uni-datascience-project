# Data Science project
This project seeks to visualize and spot trends in RIAA certifications to get a rough idea of the state of the music industry in the United States.

## Previewing
This project can be quickly viewed as a prebuilt slideshow at `./docs/visualization.slides.html`, or viewed via [GitHub Pages](https://cutotopo.github.io/uni-datascience-project/visualization.slides.html) without needing to clone the repository.

## Running
Modules should be run in the following order:
 - `riaascrape`: initial scraping of the RIAA website table endpoints
 - `musicbrainz`: lookup of scraped data using the MusicBrainz API to gather metadata that RIAA does not provide
 - `analysis`: generation of simple CSVs that can be easily visualized

This order is mostly because one module depends on the ones above it. So changes to data from `riaascrape` for example can break or change the meaning of the data from `musicbrainz` and what was generated during `analysis`.
There are `README`s in each module directory explaining how to run the modules.

## Database
This project uses a local SQLite database, `riaadb.db` for tracking data. This allows scripts to quickly get data from it as needed, with very fast filtering and grouping.

## Assumptions
For this presentation, I will use data from the following match cases:
 - all well-formed RIAA-provided data
 - an exact text match between the RIAA database and the MusicBrainz database
 - an exact text match on the artist and a fuzzy match on the recording or release title between the RIAA database and the MusicBrainz database

Data that is derived from a fuzzy match on both artist and title between the RIAA database and the MusicBrainz database will be excluded.
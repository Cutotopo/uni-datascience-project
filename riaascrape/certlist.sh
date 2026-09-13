#!/bin/bash
# Scrapes the RIAA certification database and saves the raw responses
# note: this will take a LONG time if ran start to finish
# note: this is bad code with a lot of assumptions on the server side but it does what it should do

TMPBASE=/tmp/riaadb

fetchpage() {
    CURPAGE="$1"
    curl 'https://www.riaa.com/wp-admin/admin-ajax.php?col=certification_date&ord=asc&date_option=release&tab_active=recent-award&sub_tab_active=DA' \
        --compressed \
        -X POST \
        -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0' \
        -H 'Accept: application/json, text/javascript, */*; q=0.01' \
        -H 'Accept-Language: en-US,en;q=0.9' \
        -H 'Accept-Encoding: gzip, deflate, br, zstd' \
        -H 'Referer: https://www.riaa.com/gold-%20platinum/?col=certification_date&col=certification_date&ord=asc' \
        -H 'Origin: https://www.riaa.com' \
        -H 'Connection: keep-alive' \
        -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
        -H 'X-Requested-With: XMLHttpRequest' \
        --data-raw "action=load_more_search_default&page=$CURPAGE"
}

mkdir -p $TMPBASE

echo "Writing timestamp"
date > $TMPBASE/timestamp

echo "Fetching first page..."
FIRST=$(fetchpage 1)
PAGECNT=$(echo $FIRST | jq '.total_pages')
echo $FIRST > $TMPBASE/1.json

for i in $(seq 2 $PAGECNT); do
    echo "Fetching RIAA db page: $i/$PAGECNT..."
    fetchpage $i > $TMPBASE/$i.json
    sleep .75
done

cp -r $TMPBASE ./riaadb
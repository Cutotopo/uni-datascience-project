#!/bin/bash

TMPBASE=/tmp/riaadb_m

mkdir -p $TMPBASE

echo "Writing timestamp"
date > $TMPBASE/timestamp

CURRIDX=0
TOTIDX=$(cat ../outputs/riaadata.csv | sed '1d' | wc -l)

fetchhist() {
    ELID="$1"
    curl 'https://www.riaa.com/wp-admin/admin-ajax.php' \
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
        --data-raw "action=load_detail_from_recent_timeline&id=$ELID"
}

cat ../outputs/riaadata.csv | sed '1d' | while read p; do
    CURRIDX=$((CURRIDX + 1))
    echo "========== [$CURRIDX/$TOTIDX] =========="
    CID=$(echo "$p" | cut -d ',' -f 1)
    fetchhist $CID > $TMPBASE/$CID.json
    sleep .75
done

cp -r $TMPBASE ./riaam
import json
import os

dir = "./riaadb"
lst = [j for j in os.listdir(dir) if j.endswith('.json')]
lst.reverse()

def resolve_date(str):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    year = str.split(", ")[1]
    month = months.index(str.split(" ")[0]) + 1
    date = str.split(" ")[1].split(", ")[0].replace(",", "")
    return f"{year}-{month}-{date}"

def encode_csv(str):
    str = str.replace("\n", "")
    quoted = False
    if ',' in str:
        quoted = True
    if '"' in str:
        quoted = True
        str = str.replace("\"", "\"\"")
    if quoted:
        return f"\"{str}\""
    return str

print("ID,ARTIST,TITLE,RELEASE_TYPE,CERT_DATE,CERT_LEVEL,CERT_TYPE,CERT_GOLD,CERT_PLATINUM,CERT_DIAMOND")

def parse_file(data):
    lns = data.split("<tr")
    for (i, l) in enumerate(lns):
        if i == 0:
            continue
        id = l.split("javascript:showTimeline(")[1].split(")")[0]
        artist = encode_csv(l.split("<td class='tw-artists_cell' >")[1].split("</td>")[0])
        title = encode_csv(l.split("<td class=\"others_cell\">")[1].split("</td>")[0])
        reltype = l.split("<td class=\"others_cell format_cell\">")[1].split("</td>")[0]
        certdate = resolve_date(l.split("<td class=\"others_cell tw-text-center\">")[1].split("</td>")[0])
        certlevel = int(l.split("alt=\"")[1].split(" level ")[1].split("\"")[0])
        certtype = l.split("alt=\"badge ")[1].split(" level ")[0]
        certgold = certlevel * 2 or 1
        certplat = certlevel
        certdiam = certlevel // 10
        print(f"{id},{artist},{title},{reltype},{certdate},{certlevel},{certtype},{certgold},{certplat},{certdiam}")

total = 1
cIdx = 1

while cIdx <= total:
    with open(f"{dir}/{cIdx}.json", "r") as f:
        j = json.loads(f.read())
    total = j["total_pages"]
    parse_file(j["data"])
    cIdx += 1
import json
import os

dir = "./riaam"
lst = [j for j in os.listdir(dir) if j.endswith('.json')]
lst.reverse()

def resolve_date(str):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    year = str.split(", ")[1]
    month = months.index(str.split(" ")[0]) + 1
    date = str.split(" ")[1].split(", ")[0].replace(",", "")
    return f"{year}-{month}-{date}"

def resolve_award_level(str):
    if 'X' not in str:
        str = f"1X {str}"

    awardsST = ["GOLD", "PLATINUM", "DIAMOND"]
    awardsLA = ["ORO", "PLATINO", "DIAMANTE"]

    awspl = str.split("X ")
    lvlbase = int(awspl[0])
    
    if awspl[1] == awardsST[2] or awspl[1] == awardsLA[2]: # DIAMOND
        mlt = 10
    elif awspl[1] == awardsST[0] or awspl[1] == awardsLA[0]: # GOLD
        mlt = 0 # it would be 0.5 but RIAA counts it as tier "zero"
    else:
        mlt = 1
    
    return lvlbase * mlt

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

print("RIAAID,CERT_DATE,CERT_DESCRIPTION,CERT_LEVEL")

def parse_file(data, rid):
    timelinespl = data.split('<div class="tw-molecule-timeline ">')[1]
    tlitems = timelinespl.split('<div class="tw-time-date-')
    for (i, tli) in enumerate(tlitems):
        if i == 0:
            continue

        tldate = resolve_date(tli.split('<p class="tw-tag-date">')[1].split("</p>")[0])
        tlrawawards = tli.split('<p class="tw-tag-label">')
        for (j, tlaw) in enumerate(tlrawawards):
            if j == 0:
                continue
            tlawlabel = tlaw.split("</p>")[0].replace("&nbsp;", " ")
            print(f"{rid},{tldate},{tlawlabel},{resolve_award_level(tlawlabel)}")

total = len(lst)

for (cIdx, fl) in enumerate(lst):
    # print(f"========== [{cIdx + 1}/{total}] ==========")
    # print(f"Using file: {fl}")
    with open(f"{dir}/{fl}", "r") as f:
        j = json.loads(f.read())
    parse_file(j['body'], fl.replace(".json", ""))
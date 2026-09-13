import json
import os

dir = "./riaam"
lst = [j for j in os.listdir(dir) if j.endswith('.json')]
lst.reverse()

def resolve_date(str):
    if ',' not in str:
        return "0000-00-00"
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

print("RIAAID,LABEL,GENRE,RELEASE_DATE,CERT_DATE_FIRST")

def parse_file(data, rid):
    detsplit = data.replace("&amp;", "&").split('<div class="tw-molecule-timeline-details ">')[1].strip()
    labelspl = detsplit.split('<div class="tw-text-xs tw-font-bold">Label</div><div class="tw-text-sm">')[1].split("</div>")[0].strip()
    genrespl = detsplit.split('<div class="tw-text-xs tw-font-bold">Genre</div><div class="tw-text-sm">')[1].split("</div>")[0].strip()
    releasespl = detsplit.split('<div class="tw-text-xs tw-font-bold">Released on</div><div class="tw-text-sm">')[1].split("</div>")[0].strip()
    firstcertspl = detsplit.split('<div class="tw-font-tusker tw-font-label">First Certification</div>')[1].split('div class="tw-flex tw-flex-col tw-gap-riaa-x-small"><div class="tw-text-xs tw-font-semibold">Date</div><div class="tw-text-sm">')[1].split('</div>')[0]
    print(f"{rid},{encode_csv(labelspl)},{encode_csv(genrespl)},{resolve_date(releasespl)},{resolve_date(firstcertspl)}")

total = len(lst)

for (cIdx, fl) in enumerate(lst):
    # print(f"========== [{cIdx + 1}/{total}] ==========")
    with open(f"{dir}/{fl}", "r") as f:
        j = json.loads(f.read())
    parse_file(j['body'], fl.replace(".json", ""))
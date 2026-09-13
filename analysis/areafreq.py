import csv

countrydata = {}

def csv_get_column(header, row, targ):
    i = header.index(targ)
    return row[i]

with open("../outputs/mbartist.csv", "r") as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        country = csv_get_column(header, row, "COUNTRY")

        if country not in countrydata:
            countrydata[country] = {
                'scores': {
                    'ST': 0,
                    'LA': 0,
                    'DI': 0
                },
                'totals': {
                    'leading': 0,
                    'featuring': 0
                }
            }
        
        countrydata[country]['scores']['ST'] += int(csv_get_column(header, row, "TOTAL_ST_SCORE"))
        countrydata[country]['scores']['LA'] += int(csv_get_column(header, row, "TOTAL_LA_SCORE"))
        countrydata[country]['scores']['DI'] += int(csv_get_column(header, row, "TOTAL_DI_SCORE"))
        countrydata[country]['totals']['leading'] += int(csv_get_column(header, row, "AWARDS_LEAD"))
        countrydata[country]['totals']['featuring'] += int(csv_get_column(header, row, "AWARDS_FEATURING"))

print("COUNTRY,ST_SCORE,DI_SCORE,LA_SCORE,AWARDS_LEAD,AWARDS_FEATURING")
for country in countrydata:
    data = countrydata[country]
    print(f"{country},{data['scores']['ST']},{data['scores']['DI']},{data['scores']['LA']},{data['totals']['leading']},{data['totals']['featuring']}")
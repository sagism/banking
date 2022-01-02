"""Parse Bank Leumi's html account summary and convert it into a csv

This is based on reverse-engineering the format I did early Jan 2022.
The bank also offers an xls export format but in my experience it is useless.
"""

import sys
import csv
import re

from bs4 import BeautifulSoup

try:
    infile_name = sys.argv[1]
except:
    print("first argument should be the name of the file you saved")
    raise

outfile_name = infile_name + ".csv"

writer = csv.DictWriter(open(outfile_name, "w"), 
        fieldnames=('date', 'description', 'deposit', 'withdrawal'))
writer.writeheader()

records = [] # I want to reverse the order before saving...

html_doc = open(sys.argv[1])
soup = BeautifulSoup(html_doc, 'html.parser')
for elem in soup.find_all("div", class_="ts-table-row"):
    record = {}
    date_elem = elem.find("div", attrs={"data-header": "תאריך"}) #  data_header="תאריך")
    if date_elem:
        date_span = date_elem.find("span", class_="show-exporttool")
        if date_span:
            date_str = date_span.text 
            match = re.match(r'(\d\d)/(\d\d)/(\d\d)', date_str)
            dd, mm, yy = match.groups()
            record['date'] = f'20{yy}-{mm}-{dd}'
            descr = elem.find("div", attrs={"data-header": "תיאור"})
            if descr:
                descr_span = descr.find("span")
                if descr_span:
                    record['description'] = descr_span.text
                deposit = elem.find("div", attrs={"data-header": "זכות"})
                if deposit:
                    val = deposit.find("span").text
                    fval = float(val.replace(',',''))
                    record['deposit'] = fval if abs(fval) > 0.001 else ''   
                withdrawal = elem.find("div", attrs={"data-header": "חובה"})
                if withdrawal:
                    val = withdrawal.find("span").text
                    fval = float(val.replace(',',''))
                    record['withdrawal'] = fval if abs(fval) > 0.001 else ''
                records.append(record)

records.reverse()
for record in records:
    writer.writerow(record)



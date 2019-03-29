import requests
from bs4 import BeautifulSoup
import csv


def derermineNthRecentFiling(filingUrls, n=1):
    orderedFilings = sorted([i.split("/")[-1] for i in filingUrls])[-n]
    return orderedFilings


def getCompanyFilings(cik, filingType, limit= 1):
    baseURL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=" + cik + "&type=" + filingType + "&dateb=&owner=include&count=10"
    page = requests.get(baseURL)
    tree = page.content
    return tree
    # return edgar.getDocuments(tree, limit)


def getSelectedFilingContent(cik, filingNumber):
    number = filingNumber.split("-")
    parsedNumber = number[0] + number[1] + number[2]
    originalNumber = number[0] + "-" + number[1] + "-" + number[2]
    # return number
    baseURL = "https://www.sec.gov/Archives/edgar/data/" + cik + '/' + parsedNumber + "/" + originalNumber + ".txt"
    return BeautifulSoup(requests.get(baseURL).content)


def main():
    cik = "0001166559"
    filingsPage = getCompanyFilings(cik, '13F')
    page = BeautifulSoup(filingsPage)
    filingsElements = page.find_all(id="documentsbutton")
    filingsUrls = [i.get('href') for i in filingsElements]
    desiredFiling = derermineNthRecentFiling(filingsUrls, 1)
    filingContent = getSelectedFilingContent(cik, desiredFiling)
    informationTable = filingContent.find('informationtable')
    data = []
    cols = []
    infoRows = informationTable.findAll('infotable')
    for item in infoRows:
        for elem in item:
            if elem != '\n':
                if elem.name not in cols:
                    cols.append(elem.name)
    for item in infoRows:
        rowData = ["N/A" ] * len(cols)
        for elem in item:
            if elem != '\n':
                rowData[cols.index(elem.name)] = elem.text
        data.append(rowData)
    print(cols, data)


    with open('output.tsv', 'wt') as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t')
        tsv_writer.writerow(cols)
        for i in range(len(data)):
            tsv_writer.writerow(data[i])
        out_file.close()


if __name__ == "__main__":
    main()

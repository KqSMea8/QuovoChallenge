import requests
from bs4 import BeautifulSoup
import csv


def derermineNthRecentFiling(filingUrls, n=1):
    if len(filingUrls) < n:
        return "Not enough filings"
    orderedFilings = sorted([i.split("/")[-1] for i in filingUrls])[-n]
    return orderedFilings


def getCompanyFilings(cik, filingType, limit= 1):
    baseURL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=" + cik + "&type=" + filingType + "&dateb=&owner=include&count=10"
    page = requests.get(baseURL)
    tree = page.content
    return tree


def getSelectedFilingContent(cik, filingNumber):
    filingNumber = filingNumber.split("-")
    parsedNumber = filingNumber[0] + filingNumber[1] + filingNumber[2]
    originalNumber = filingNumber[0] + "-" + filingNumber[1] + "-" + filingNumber[2]
    baseURL = "https://www.sec.gov/Archives/edgar/data/" + cik + '/' + parsedNumber + "/" + originalNumber + ".txt"
    return BeautifulSoup(requests.get(baseURL).content, features="lxml")

def sanitizeData(data):
    sanData = []
    for item in data:
        sanRow = []
        for i in item:
            sanRow.append(i.replace("\n", " "))
        sanData.append(sanRow)
    return sanData


def main():
    cik = "0001462245"
    filingsPage = getCompanyFilings(cik, "13F")
    page = BeautifulSoup(filingsPage, features="lxml")
    # get all filings Ids
    filingsElements = page.find_all(id="documentsbutton")
    filingsUrls = [i.get("href") for i in filingsElements]
    # get most recent filing, change 1 to desired filing
    desiredFiling = derermineNthRecentFiling(filingsUrls, 1)
    if desiredFiling == "Not enough filings":
        return (print('404 Filing not found'))
    filingContent = getSelectedFilingContent(cik, desiredFiling)
    #retrieve information table from text page
    informationTable = filingContent.find("informationtable")

    data = []
    cols = []
    infoRows = informationTable.findAll("infotable")
    #find columns
    for item in infoRows:
        for elem in item:
            if elem != "\n":
                if elem.name not in cols:
                    cols.append(elem.name)
    #create list of rows corresponding to columns
    for item in infoRows:
        rowData = ["N/A" ] * len(cols)
        for elem in item:
            if elem != "\n":
                rowData[cols.index(elem.name)] = elem.text.strip()
        data.append(rowData)
    sanData = sanitizeData(data)

    with open("output0001462245.tsv", "wt") as out_file:
        tsv_writer = csv.writer(out_file, delimiter="\t")
        tsv_writer.writerow(cols)
        for i in range(len(sanData)):
            tsv_writer.writerow(sanData[i])
        out_file.close()


if __name__ == "__main__":
    main()


import requests
import json


RequestPayload = {
    "page": 1,
    "rowsInPage": 50,
    "nameFilter": "",
    "kpiFilter": [
        {"kpiId": 7, "calculation": 0, "calcTime": 0, "categoryId": 11,
            "calculationType": 3, "lowPrice": None, "highPrice": None},
        {"kpiId": 151, "calculation": 20, "calcTime": 1, "categoryId": 9,
            "calculationType": 2, "lowPrice": None, "highPrice": None},
        {"kpiId": 151, "calculation": 20, "calcTime": 6, "categoryId": 9,
            "calculationType": 2, "lowPrice": None, "highPrice": None},
        {"kpiId": 1, "calculation": 1, "calcTime": 0, "categoryId": 0,
            "calculationType": 2, "lowPrice": None, "highPrice": None},
        {"kpiId": 2, "calculation": 1, "calcTime": 0, "categoryId": 0,
            "calculationType": 2, "lowPrice": None, "highPrice": None},
        {"kpiId": 3, "calculation": 1, "calcTime": 0, "categoryId": 0,
            "calculationType": 2, "lowPrice": None, "highPrice": None},
        {"kpiId": 4, "calculation": 1, "calcTime": 0, "categoryId": 0,
            "calculationType": 2, "lowPrice": None, "highPrice": None},
        {"kpiId": 12, "calculation": 0, "calcTime": 0, "categoryId": 11,
            "calculationType": 3, "lowPrice": None, "highPrice": None},
        {"kpiId": 2, "calculation": 0, "calcTime": 0, "categoryId": 11,
            "calculationType": 3, "lowPrice": None, "highPrice": None},
        {"kpiId": 1, "calculation": 0, "calcTime": 0, "categoryId": 11,
            "calculationType": 3, "lowPrice": None, "highPrice": None},
        {"kpiId": 5, "calculation": 0, "calcTime": 0, "categoryId": 11,
            "calculationType": 3, "lowPrice": None, "highPrice": None}
    ],
    "watchlistId": None,
    "selectedCountries": [1, 2, 3, 4],
    "companyNameOrdering": 0
}


def GetPatComapnyPage(pageNR, ):

    API_Endpoint = "https://borsdata.se/api/terminal/screener/kpis/data"
    reqBody = RequestPayload
    reqBody["page"] = pageNR

    ReturnJSON = ""
    ComapnyRequest = requests.post(url=API_Endpoint, json=reqBody)
    try:
        if ComapnyRequest.status_code == 200:
            Data = ComapnyRequest.json()
            ReturnJSON = Data
        else:
            print(ComapnyRequest.text)
            raise Exception()
    except Exception as e:
        print(f'Error: {e}')
        raise Exception
    return ReturnJSON


def GetPatComapnyHistory(CompanyShotname, fromDate, toDate, countback):

    # https://borsdata.se/api/terminal/instruments/abelco-investment-group
    # https://borsdata.se/api/terminal/ta/history?symbol=24STOR&resolution=1D&from=1581756619&to=1639212679
    # https://borsdata.se/api/terminal//instruments/1871/stockprices?format=chart

    API_Endpoint = 'https://borsdata.se/api/terminal/ta/history?symbol=' + \
        str(CompanyShotname) + '&resolution=1D&from=' + str(fromDate) + \
        '&to=' + str(toDate) + '&countback=' + str(countback)
    ComapnyRequest = requests.get(url=API_Endpoint)
    ReturnJSON = ""
    try:
        ReturnJSON = ComapnyRequest.json()
    except Exception as e:
        print(f'Error: {e}')
    return ReturnJSON

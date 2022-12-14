from msilib.schema import Error
from sqlite3 import Timestamp


from Api import *
from helper.MiscFunctions import *
from datetime import datetime, timezone, timedelta, tzinfo
import time
import pytz

import os
import json
import requests

from bs4 import BeautifulSoup
from dateutil.parser import parse
from crawler.models import *
1
# GDC = GetDataClass
# GDC.GetCompanyList()
# GDC.GetAllStockHistory()
# GDC.getworldkpi()
# GDC.WriteDataForTraining()


class DataCrawler:
    def __init__(self, CollctorSettingsName=None):
        super(DataCrawler, self).__init__()
        if(CollctorSettingsName == None):
            print('Gerting default colletor')
            try:
                self.settings = CollectorSettings.objects.get(collectionName='')
            except CollectorSettings.DoesNotExist:
                
                self.settings = CollectorSettings.objects.create(collectionName='')
            except Exception as e:
                print(e)
                raise Exception('no collection settings')
        else:    
            try:
                self.settings = CollectorSettings.objects.get(collectionName=CollctorSettingsName)
            except CollectorSettings.DoesNotExist:
                self.settings = CollectorSettings.objects.create(collectionName=CollctorSettingsName)
          
                
        now = datetime.now().replace(tzinfo=pytz.utc)
        self.settings.collectionTimestamp = now
        self.settings.completeColletion = False
        self.settings.firstInculdedDate = (now - timedelta(days=(self.settings.daysToCollect))).replace(hour=0, minute=0, tzinfo=pytz.utc)
        self.settings.lastIncudedDate = now.replace(hour=0, minute=0, tzinfo=pytz.utc)
        self.settings.save()

    def utcformat(self, dt, timespec="milliseconds"):
        """convert datetime to string in UTC format (YYYY-mm-ddTHH:MM:SS.mmmZ)"""
        iso_str = dt.astimezone(timezone.utc).isoformat("T", timespec)
        return iso_str.replace("+00:00", "Z")

    def parsetime(self, s):
        try:
            ret = parse(s)
        except ValueError:
            ret = datetime.utcfromtimestamp(s)
        except Exception as e:
            ret = datetime.fromtimestamp(s / 1000, pytz.utc)
        return ret

    def getworldkpi(self):
        WorldKPIJson = {}
        getpage = requests.get("https://www.avanza.se/marknadsoversikt.html")
        soup = BeautifulSoup(getpage.text, "html.parser")

        nowsecstr = str(
            int(datetime.timestamp(datetime.now().replace(tzinfo=pytz.utc)))
        )

        # Mydate = GetDataClass.parsetime(nowsecstr)
        # strsecondssinceepoch = str(int((Mydate - datetime(1970, 1, 1).replace(tzinfo=pytz.UTC)).totalseconds()*1000))

        for group in soup.findAll("optgroup"):
            WorldKPIJson[group.attrs["label"]] = {}
            for opt in group.findAll("option"):
                try:
                    customlabel = opt.text.replace(
                        "\r\n\t                               ", ""
                    )

                    WorldKPIJson[group.attrs["label"]][customlabel] = {}
                    WorldKPIJson[group.attrs["label"]][customlabel][
                        "value"
                    ] = opt.attrs["value"]

                    subpage = requests.get(
                        "https://www.avanza.se/ab/component/indexperformance/marketoverview/"
                        + opt.attrs["value"]
                        + "?_="
                        + nowsecstr
                    )
                    subsoup = BeautifulSoup(subpage.text, "html.parser")
                    WorldKPIJson[group.attrs["label"]][customlabel]["timeperiods"] = []
                    for i in subsoup.find_all("li"):
                        datas = BeautifulSoup(str(i), "html.parser")
                        for a in datas.find_all("a"):
                            WorldKPIJson[group.attrs["label"]][customlabel][
                                "timeperiods"
                            ].append(a.attrs["data-timeperiod"])

                    thisurl = "https://www.avanza.se/ab/component/highstockchart/getchart/orderbook"
                    thisbody = {
                        "orderbookId": WorldKPIJson[group.attrs["label"]][customlabel][
                            "value"
                        ],
                        "chartType": "AREA",
                        "widthOfPlotContainer": 640,
                        "chartResolution": "DAY",
                        "navigator": "false",
                        "percentage": "false",
                        "volume": "false",
                        "owners": "false",
                        "start": self.utcformat(self.settings.firstInculdedDate),
                        "end": self.utcformat(datetime.now()),
                        "ta": [],
                    }
                    # thisbody = {
                    #     "orderbookId": WorldKPIJson[group.attrs['label']][customlabel]['value'],
                    #     "chartType": "AREA",
                    #     "chartResolution": "DAY",
                    #     "widthOfPlotContainer": 312,
                    #     "navigator": False,
                    #     "volume": False,
                    #     "compareIds": [],
                    #     "percentage": False,
                    #     "start": str(SettingsObject.firstInculdedDate.replace(tzinfo=pytz.utc)),
                    #     "end": str(datetime.now().replace(tzinfo=pytz.utc)),
                    #     "ta": [],

                    # } 

                    chartrequest = requests.get(thisurl, json=thisbody)
                    data = json.loads(chartrequest.text)
                    WorldKPIJson[group.attrs["label"]][customlabel]["data"] = {}
                    for indexKpi, dataPoint in enumerate(data["dataPoints"]):

                        mydate = datetime.fromtimestamp(
                            dataPoint[0] / 1000, pytz.utc
                        ).date()
                        # mydate = mydate.replace(hour = 0, minute=0, tzinfo= pytz.utc) #sommaRTIDER

                        # StocksjsoninMemory[thiscompany][str(mydate)] = {}
                        if dataPoint[1] != None:
                            WorldKPIJson[group.attrs["label"]][customlabel]["data"][
                                str(mydate)
                            ] = dataPoint[1]
                            backcounter = 1
                            yesterday = mydate - timedelta(days=1)
                            Lastknownprice = -1
                            if ( 
                                len(
                                    WorldKPIJson[group.attrs["label"]][customlabel][
                                        "data"
                                    ]
                                )
                                > 1
                            ):
                                while (
                                    not str(yesterday)
                                    in WorldKPIJson[group.attrs["label"]][customlabel][
                                        "data"
                                    ]
                                ):
                                    if (
                                        yesterday
                                        <= self.settings.firstInculdedDate.date()
                                    ):
                                        Lastknownprice = 0
                                        break
                                    yesterday = yesterday - timedelta(days=1)
                                    backcounter += 1

                                if Lastknownprice != 0:
                                    Lastknownprice = WorldKPIJson[group.attrs["label"]][
                                        customlabel
                                    ]["data"][str(yesterday)]

                                AvrageChange = (
                                    WorldKPIJson[group.attrs["label"]][customlabel][
                                        "data"
                                    ][str(mydate)]
                                    - Lastknownprice
                                ) / backcounter

                                dayAfter = yesterday + timedelta(days=1)
                                while (
                                    not str(dayAfter)
                                    in WorldKPIJson[group.attrs["label"]][customlabel][
                                        "data"
                                    ]
                                ):

                                    WorldKPIJson[group.attrs["label"]][customlabel][
                                        "data"
                                    ][str(dayAfter)] = (
                                        WorldKPIJson[group.attrs["label"]][customlabel][
                                            "data"
                                        ][str(dayAfter - timedelta(days=1))]
                                        + AvrageChange
                                    )
                                    dayAfter = dayAfter + timedelta(days=1)
                            else:
                                WorldKPIJson[group.attrs["label"]][customlabel]["data"][
                                    str(mydate)
                                ] = -1
                        else:
                            WorldKPIJson[group.attrs["label"]][customlabel]["data"][
                                str(mydate)
                            ] = -1
                except Exception as e:
                    print(e)
                print(f"Group: {group} option: {customlabel} done")
            time.sleep(0.5)

        for _group in WorldKPIJson:
            for _name in WorldKPIJson[_group]:
                if "data" in WorldKPIJson[_group][_name]:
                    for _date in WorldKPIJson[_group][_name]["data"]:
                        try:
                            KPIpoint = WorldKPI.objects.get_or_create(
                                group=_group,
                                name=_name,
                                timestamp=datetime.strptime(_date, "%Y-%m-%d").replace(
                                    tzinfo=pytz.utc
                                ),
                                value=WorldKPIJson[_group][_name]["data"][_date],
                            )

                        except Exception as e:
                            print(e)
                    print(_group, _name)
        print("done")

    def GetCompanyList(self):

        MyCompanys = {}

        MyCompanysReturned = {"Start": "start"}
        LastcompanyId = -1

        MyCompanysCounter = -1
        NumberofComapnys = 0

        print("Starting Comapany Collection.....")

        kpisValuesIndex = {
            "onedaydiff": 1,
            "oneyearddiff": 2,
            "directavkastning": 3,
            # Direktavkastning ??r ett bolags aktieutdelning i f??rh??llande till aktiekursen och ett m??tt p?? avkastningen till aktie??garna. Snittet f??r direktavkastning brukar ligga mellan 2,7 % - 4,1 %. Direktavkastningen r??knas genom: (Utdelning per Aktie / Aktiekurs)
            "PE": 4,
            # P/E- tal st??r f??r 'Price/Earnings' vilket betyder Aktiekurs/Vinst. Nyckeltalet anv??nds n??r man ska bed??ma aktiens v??rdering i f??rh??llande till f??retagets vinst och ett P/E - tal p?? 10 betyder att man betalar 10 g??nger ??rsvinsten f??r en aktie. Snittet f??r P/E-tal brukar ligga mellan 12 - 16 och r??knas genom: (Aktiekurs / Vinst Per Aktie )
            "PS": 5,
            # P/S st??r f??r 'Price/Sales' vilket betyder Aktiekurs/Oms??ttning. Nyckeltalet anv??nds n??r man ska bed??ma hur mycket varje oms??ttningskrona v??rderas i f??rh??llande till aktiekursen. Snittet f??r P/S-tal brukar ligga mellan 0,9 - 3,1 och varierar kraftigt beroende p?? oms??ttningens l??nsamhet. P/S r??knas genom: (Aktiekurs/Oms??ttning Per Aktie)
            "PB": 6,
            # P/B- tal st??r f??r 'Price/Bookvalue' vilket betyder Aktiekurs/eget kapital. Nyckeltalet anv??nds till att visa hur f??retagets eget kapital v??rderas i relation till aktiekursen. Snittet f??r P/B-tal brukar ligga mellan 1,4 - 2,4 och varierar kraftigt beroende p?? hur kapitalintensivt f??retaget ??r och tillg??ngarnas l??nsamhet. (Aktiekurs/Eget Kapital Per Aktie)
            "kpitime": 7,  # Time-part
            "kpidate": 8,  # Date-part
            # The date the Kpis were valid
        }

        while MyCompanysReturned != "":
            MyCompanysCounter = MyCompanysCounter + 1
            print(
                f"****************  Fetching company {MyCompanysCounter*100}-{(MyCompanysCounter+1)*100} *************"
            )
            MyCompanysReturned = GetPatComapnyPage(MyCompanysCounter)
            TotalFilteredComapnys = MyCompanysReturned["totalFiltered"]
            TotalCompanys = MyCompanysReturned["total"]
            MyCompanysReturned = MyCompanysReturned["data"]
            try:
                if len(MyCompanysReturned) == 0:
                    break
                elif MyCompanysReturned[0]["companyId"] == LastcompanyId:
                    break
                else:
                    LastcompanyId = MyCompanysReturned[0]["companyId"]
            except Exception as e:
                print(f"Exception: {e}")
                break
            for company in MyCompanysReturned:
                NumberofComapnys = NumberofComapnys + 1
                if company["name"].lower() not in MyCompanys:
                    MyCompanys[company["name"].lower()] = {}
                try:
                    MyCompanys[company["name"].lower()]["companyId"] = company[
                        "companyId"
                    ]
                    MyCompanys[company["name"].lower()]["countryId"] = company[
                        "countryId"
                    ]
                    MyCompanys[company["name"].lower()]["marketId"] = company[
                        "marketId"
                    ]
                    MyCompanys[company["name"].lower()]["sectorId"] = company[
                        "sectorId"
                    ]
                    MyCompanys[company["name"].lower()]["branchId"] = company[
                        "branchId"
                    ]
                    MyCompanys[company["name"].lower()]["countryUrlName"] = company[
                        "countryUrlName"
                    ].lower()
                    MyCompanys[company["name"].lower()]["shortName"] = company[
                        "shortName"
                    ]

                except Exception as e:
                    print(e)
                    continue

            print(
                f"***** {(NumberofComapnys/TotalFilteredComapnys)*100}% of {TotalFilteredComapnys} comapnys fetched. Totally there is {TotalCompanys} online.."
            )

        for company in MyCompanys:
            try:
                thisCompany = Companies.objects.get(name=company)
                thisCompany.companyId=MyCompanys[company]["companyId"]
                thisCompany.countryId=MyCompanys[company]["countryId"]
                thisCompany.marketId=MyCompanys[company]["marketId"]
                thisCompany.sectorId=MyCompanys[company]["sectorId"]
                thisCompany.branchId=MyCompanys[company]["branchId"]
                thisCompany.countryUrlName=MyCompanys[company]["countryUrlName"]
                thisCompany.shortName=MyCompanys[company]["shortName"]
                thisCompany.save()
            except Companies.DoesNotExist:
                try:
                    thisCompany = Companies.objects.create(
                        name=company,
                        companyId=MyCompanys[company]["companyId"],
                        countryId=MyCompanys[company]["countryId"],
                        marketId=MyCompanys[company]["marketId"],
                        sectorId=MyCompanys[company]["sectorId"],
                        branchId=MyCompanys[company]["branchId"],
                        countryUrlName=MyCompanys[company]["countryUrlName"],
                        shortName=MyCompanys[company]["shortName"],
                    )
                except:
     
                    continue
            except:
                continue  
            try:
                self.settings.comapnys.get(id= thisCompany.id)
            except Companies.DoesNotExist:
                self.settings.comapnys.add(thisCompany)
                self.settings.save()
                    
            except Exception as e:
                print(e)

    def GetAllStockHistory(self):

        Grandstart = time.time()
        StocksjsoninMemory = {}
        companysectorbrachsummery = {}

        MyCompanys = self.settings.comapnys.all()
        CreatingCollection = (self.settings.collectionName == '')

        TotalNumberOfCompanies = MyCompanys.count()

        if TotalNumberOfCompanies > 0:
            Counter = 0
            from_string = str(int(datetime.timestamp(self.settings.firstInculdedDate)))
            to_string = str(int(datetime.timestamp(self.settings.lastIncudedDate)))
            for indexstart, thiscompany in enumerate(MyCompanys):

                CompanyRDIIntervall = []
                if not thiscompany.name in StocksjsoninMemory:
                    StocksjsoninMemory[thiscompany.name] = {}
                StocksjsoninMemory[thiscompany.name]["UsableData"] = False
                try:
                    # if 'sectorId' in MyCompanys[thiscompany] and 'branchId' in MyCompanys[thiscompany]:
                    #     if not MyCompanys[thiscompany]['sectorId'] in companysectorbrachsummery:
                    #         companysectorbrachsummery[MyCompanys[thiscompany]['sectorId']] = {
                    #         }
                    #     if not MyCompanys[thiscompany]['branchId'] in companysectorbrachsummery[MyCompanys[thiscompany]['sectorId']]:
                    #         companysectorbrachsummery[MyCompanys[thiscompany]
                    #                                   ['sectorId']][MyCompanys[thiscompany]['branchId']] = []
                    #     companysectorbrachsummery[MyCompanys[thiscompany]['sectorId']
                    #                               ][MyCompanys[thiscompany]['branchId']].append(thiscompany)

                    print(f"looking at {thiscompany.name}", end="\r")
                    Missingdiffs = 0
                    # smallstart = time.time()
                    Counter += 1


                    History = GetPatComapnyHistory(
                        thiscompany.shortName,
                        from_string,
                        to_string,
                        self.settings.daysToCollect,
                    )
                    if(CreatingCollection):
                        if len(History["t"]) < self.settings.daysToCollect:
                            print("", end="\r")
                            print(f"looking at {thiscompany.name} ...To little data")
                            StocksjsoninMemory.pop(thiscompany.name, None)
                            self.settings.comapnys.remove(thiscompany)
                            self.settings.save()
                            
                            continue

                    removedstocklencounter = 0

                    Created = 1
                    totalpoints = 1
                    firstdatapintwritten = False
                    if( thiscompany.name == 'investment ab spiltan'):
                        x=99
                    for index, datepoint in enumerate(History["t"]):
                        totalpoints += 1
                        mydate = datetime.fromtimestamp(datepoint, pytz.utc).date()
                        # data before first date
                        if mydate < self.settings.firstInculdedDate.date():
                            print(f"{mydate} is before {self.settings.firstInculdedDate.date()}  for comapny {thiscompany.name}....")
                            continue

                        StocksjsoninMemory[thiscompany.name][str(mydate)] = {}
                        # first datapoint is later than firstincluded...
                        if (not firstdatapintwritten and mydate > self.settings.firstInculdedDate.date()):
                    
                            StockDate =  self.settings.firstInculdedDate.date()
                            while (StockDate < mydate):
                
                                StocksjsoninMemory[thiscompany.name][str(StockDate)] = {}
                                StocksjsoninMemory[thiscompany.name][str(StockDate)]["close"] = History["c"][index]
                                StocksjsoninMemory[thiscompany.name][str(StockDate)]["Rsi"] = 1
                                StocksjsoninMemory[thiscompany.name][str(StockDate)]["open"] = History["o"][index]
                                StocksjsoninMemory[thiscompany.name][str(StockDate)]["high"] = History["h"][index]
                                StocksjsoninMemory[thiscompany.name][str(StockDate)]["low"] = History["l"][index]
                                StocksjsoninMemory[thiscompany.name][str(StockDate)]["volume"] = History["v"][index]
                                StocksjsoninMemory[thiscompany.name][str(StockDate)]["daydiff_volume"] = 1
                                StockDate = StockDate + timedelta(days=1)
                        
                        #last datapoint is not lastincluded        
                        if (index+1 == (len(History["t"])) and mydate < self.settings.lastIncudedDate.date()):
                            if(CreatingCollection):
                                print(f"{thiscompany.name} last datapoint is earlier than lastincluded, removed from StocksjsoninMemory.....")
                                StocksjsoninMemory.pop(thiscompany.name, None)
                                continue
                            else:
                                StockDate =  mydate
                                while (StockDate < self.settings.lastIncudedDate.date()):
                   
                                    StocksjsoninMemory[thiscompany.name][str(StockDate)] = {}
                                    StocksjsoninMemory[thiscompany.name][str(StockDate)]["close"] = History["c"][index]
                                    StocksjsoninMemory[thiscompany.name][str(StockDate)]["Rsi"] = 1
                                    StocksjsoninMemory[thiscompany.name][str(StockDate)]["open"] = History["o"][index]
                                    StocksjsoninMemory[thiscompany.name][str(StockDate)]["high"] = History["h"][index]
                                    StocksjsoninMemory[thiscompany.name][str(StockDate)]["low"] = History["l"][index]
                                    StocksjsoninMemory[thiscompany.name][str(StockDate)]["volume"] = History["v"][index]
                                    StocksjsoninMemory[thiscompany.name][str(StockDate)]["daydiff_volume"] = 1
                                    StockDate = StockDate + timedelta(days=1)    
                            

        

                        
                        StocksjsoninMemory[thiscompany.name][str(mydate)]["open"] = History["o"][index]
                        StocksjsoninMemory[thiscompany.name][str(mydate)]["close"] = History["c"][index]
                        StocksjsoninMemory[thiscompany.name][str(mydate)]["high"] = History["h"][index]
                        StocksjsoninMemory[thiscompany.name][str(mydate)]["low"] = History["l"][index]
                        StocksjsoninMemory[thiscompany.name][str(mydate)]["volume"] = History["v"][index]
                        Histotycounter = 0
                        
                        firstdatapintwritten = True
                        
                        while History["v"][index] == 0:
                            History["v"][index] = History["v"][
                                index - 1 - Histotycounter
                            ]
                            Histotycounter = Histotycounter - 1

                        StocksjsoninMemory[thiscompany.name][str(mydate)]["daydiff_volume"] = (History["o"][index] - History["c"][index]) / History["v"][
                            index
                        ]

                        CompanyRDIIntervall.append(
                            StocksjsoninMemory[thiscompany.name][str(mydate)]["close"]
                        )

                        while len(CompanyRDIIntervall) > self.settings.RSIintervall:
                            CompanyRDIIntervall.pop(0)
                        ups = 1
                        downs = 1
                        if len(CompanyRDIIntervall) == self.settings.RSIintervall:
                            for day in range(len(CompanyRDIIntervall) - 1):
                                if day > 0:
                                    RDItoday = (
                                        CompanyRDIIntervall[day]
                                        / CompanyRDIIntervall[day - 1]
                                    )
                                    if RDItoday > 1:
                                        if ups == 1:
                                            ups = 0
                                        ups = ups + RDItoday
                                    elif RDItoday < 1:
                                        if downs == 1:
                                            downs = 0
                                        downs = downs + RDItoday

                        else:
                            ups = 1
                            downs = 1

                        rs = ups / downs
                        rsi = 100 - (100 / (1 + rs))
                        StocksjsoninMemory[thiscompany.name][str(mydate)]["Rsi"] = rsi

                        if len(StocksjsoninMemory[thiscompany.name]) > 2:

                            backcounter = 1
                            yesterday = mydate - timedelta(days=1)
                            while (not str(yesterday) in StocksjsoninMemory[thiscompany.name]):
                                if yesterday <= self.settings.firstInculdedDate.date():
                                    break

                                yesterday = yesterday - timedelta(days=1)
                                backcounter += 1
                                
                            Lastknownprice = StocksjsoninMemory[thiscompany.name][str(yesterday)]["close"]
                            AvrageChange = (
                                StocksjsoninMemory[thiscompany.name][str(mydate)][
                                    "close"
                                ]
                                - Lastknownprice
                            ) / backcounter

                            dayAfter = yesterday + timedelta(days=1)
                            while (not str(dayAfter) in StocksjsoninMemory[thiscompany.name]):
                                StocksjsoninMemory[thiscompany.name][str(dayAfter)] = {}
                                StocksjsoninMemory[thiscompany.name][str(dayAfter)]["close"] = (StocksjsoninMemory[thiscompany.name][str(dayAfter - timedelta(days=1))]["close"]+ AvrageChange)
                                StocksjsoninMemory[thiscompany.name][str(dayAfter)]["Rsi"] = StocksjsoninMemory[thiscompany.name][str(dayAfter - timedelta(days=1))]["Rsi"]
                                StocksjsoninMemory[thiscompany.name][str(dayAfter)]["open"] = StocksjsoninMemory[thiscompany.name][str(dayAfter - timedelta(days=1))]["open"]
                                StocksjsoninMemory[thiscompany.name][str(dayAfter)]["high"] = StocksjsoninMemory[thiscompany.name][str(dayAfter - timedelta(days=1))]["high"]
                                StocksjsoninMemory[thiscompany.name][str(dayAfter)]["low"] = StocksjsoninMemory[thiscompany.name][str(dayAfter - timedelta(days=1))]["low"]
                                StocksjsoninMemory[thiscompany.name][str(dayAfter)]["volume"] = StocksjsoninMemory[thiscompany.name][str(dayAfter - timedelta(days=1))]["volume"]
                                StocksjsoninMemory[thiscompany.name][str(dayAfter)]["daydiff_volume"] = StocksjsoninMemory[thiscompany.name][str(dayAfter - timedelta(days=1))]["daydiff_volume"]
                                dayAfter = dayAfter + timedelta(days=1)

                    totallemn = index - removedstocklencounter
                    RatioDataCreated = (Created / totallemn) * 100
                    UsableData = False
                    if RatioDataCreated <= self.settings.ValidStockdataLimit:
                        UsableData = True
                    StocksjsoninMemory[thiscompany.name]["UsableData"] = UsableData
                except Exception as e:
                    try:
                        print(e)
                        print(f"at {index} in {thiscompany.name}, removed from StocksjsoninMemory")
                        currentcomapny = Companies.objects.get(name = thiscompany.name)
                        self.settings.comapnys.remove(currentcomapny)
                        StocksjsoninMemory.pop(thiscompany.name, None)
                        continue
                    except Exception as e:
                        print(e)
                        raise Exception('Cant remove company from collection')
                SmallEnd = time.time()
                ELAPSED = SmallEnd - Grandstart
                AVRAGE = ELAPSED / Counter
                ETA = (TotalNumberOfCompanies - Counter) * (ELAPSED / Counter)
                PROGRESS = (Counter / TotalNumberOfCompanies) * 100

                print(
                    f"****************                            StockDownloaded                     ************************"
                )
                print(
                    f"*   Company: {thiscompany.name}                                                              "
                )
                print(
                    f"*   Elapsed time: {ELAPSED}s with an avrage time per loop:{AVRAGE}s                                     "
                )
                print(
                    f"*   MissingDiffs: {Missingdiffs}                                                                        "
                )
                print(
                    f"*   Created: {RatioDataCreated}%, Valid data: {UsableData}                                                           "
                )
                print(
                    f"*   {PROGRESS}% done giving an ETA in {ETA}s                                                            "
                )
                print(
                    f"*                                                                                                       "
                )
                print(
                    f"****************                           *********                            ************************"
                )
                print(f" ")
                print(f" ")

            # print(f'Writing company sector branch to disk......')
            # if (os.path.exists(SettingsObject.CompanysecbraFile)):
            #     os.remove(SettingsObject.CompanysecbraFile)
            # OverWriteJson(SettingsObject.CompanysecbraFile,
            #               companysectorbrachsummery)

            print(f"Writing stocksfile to disk......")
            # if (os.path.exists(SettingsObject.StocksFile)):
            #     os.remove(SettingsObject.StocksFile)
            # OverWriteJson(SettingsObject.StocksFile, StocksjsoninMemory)
            expecteingstocklen = -1
            for index3, comapnystock in enumerate(StocksjsoninMemory):
                print(index3, " writing stock to db... ", comapnystock)
                stockcount = -1
                if(comapnystock == 'investment ab spiltan'):
                    x = 99
                for datapointday in StocksjsoninMemory[comapnystock]:

                    # comapny = models.ForeignKey(Companies, on_delete=models.DO_NOTHING)
                    # timestamp = models.DateTimeField(default=None, blank=True)
                    # close = models.FloatField(default=-1)
                    # open = models.FloatField(default=-1)
                    # high = models.FloatField(default=-1)
                    # low = models.FloatField(default=-1)
                    # volume = models.FloatField(default=-1)
                    # daydiff_volume = models.FloatField(default=-1)
                    if datapointday != "UsableData":
                        stockcount += 1
                        try:
                  
                            CompanyStockDay.objects.get(timestamp=datetime.strptime(datapointday, "%Y-%m-%d").replace(tzinfo=pytz.utc))
                        except CompanyStockDay.DoesNotExist: 
                            CompanyStockDay.objects.create(
                                comapny=Companies.objects.get(name=comapnystock),
                                timestamp=datetime.strptime(datapointday, "%Y-%m-%d").replace(tzinfo=pytz.utc),
                                close=StocksjsoninMemory[comapnystock][datapointday]["close"],
                                open=StocksjsoninMemory[comapnystock][datapointday]["open"],
                                high=StocksjsoninMemory[comapnystock][datapointday]["high"],
                                low=StocksjsoninMemory[comapnystock][datapointday]["low"],
                                volume=StocksjsoninMemory[comapnystock][datapointday]["volume"],
                                daydiff_volume=StocksjsoninMemory[comapnystock][datapointday]["daydiff_volume"],
                            )
                if index3 == 0:
                    expecteingstocklen = stockcount
  
                if stockcount != expecteingstocklen:
                    print(
                        f"Anomaly {comapnystock}, got  {stockcount} stocks, expeted {expecteingstocklen}"
                    )
                    try:
                        
                        thisCompany = Companies.objects.get(name=comapnystock)
                        thisCompany.corruptData = True
                        thisCompany.save()
                        self.settings.comapnys.remove(thisCompany)
                        self.settings.save()
                    except Exception as e:
                        print(e)
                        raise Exception(
                            "Critial Error, cant render companyData as corrupt"
                        )
                else:
                    try:
                        thisCompany = Companies.objects.get(name=comapnystock)
                        thisCompany.corruptData = False
                        thisCompany.save()
                    except Exception as e:
                        print(e)
                        raise Exception("Critial Error, cant render companyData as OK")

            print(f"StockCollection Done...")


    def do(self):
        #New Collector
        if self.settings.collectionName == '':
            self.settings.completeCollection = False
            self.settings.save()
            
            #self.GetCompanyList()
            self.GetAllStockHistory()
            #self.getworldkpi()
            
            collectionregCunter = str(CollectorSettings.objects.all().count())
            self.settings.collectionName = 'Collection_' + collectionregCunter
            self.settings.completeCollection = True
            self.settings.save()
        else:
            self.settings.completeCollection = False
            self.settings.save()
            self.GetAllStockHistory()   
            self.settings.completeCollection = True
            self.settings.save()         

 # Graveyard

            # for indexWrite, thisKPI in enumerate(MyKPI):

            #     for index2, thisSubKPI in enumerate(MyKPI[thisKPI]):
            #         try:
            #             thisrow.append(
            #                 MyKPI[thisKPI][thisSubKPI]['data'][str(trainingdate)])
            #             # print(MyKPI[thisKPI][thisSubKPI]['data'][str(trainingdate)])
            #             if (daycounter == 1):
            #                 SettingsObject.KPIwidth = SettingsObject.KPIwidth + 1
            #                 SettingsObject.firstkpiday = str(trainingdate)

            #         except Exception as e:
            #             if (daycounter > SettingsObject.lookToTheFuture):
            #                 trainingdateyesterday = trainingdate - \
            #                     timedelta(days=1)
            #                 while not trainingdateyesterday.strftime("%Y-%m-%d") in MyKPI[thisKPI][thisSubKPI]['data']:

            #                     if(trainingdateyesterday < SettingsObject.firstInculdedDate):
            #                         MyKPI[thisKPI][thisSubKPI]['data'][trainingdateyesterday.strftime(
            #                             "%Y-%m-%d")] = 0
            #                         break
            #                     trainingdateyesterday = trainingdateyesterday - \
            #                         timedelta(days=1)
            #                 thisrow.append(
            #                     MyKPI[thisKPI][thisSubKPI]['data'][trainingdateyesterday.strftime("%Y-%m-%d")])
            #             else:
            #                 thisrow.append(0)

            #             if (daycounter == 1):
            #                 SettingsObject.KPIwidth = SettingsObject.KPIwidth + 1
            #                 SettingsObject.firstkpiday = str(trainingdate)

            # if (daycounter == 1):
            #     SettingsObject.save()
            # strtrainingdate = trainingdate.strftime("%Y-%m-%d")
            # strPredict_lookback = (
            #     trainingdate - timedelta(days=SettingsObject.lookToTheFuture)).strftime("%Y-%m-%d")
            # strprediction = (
            #     trainingdate + timedelta(days=SettingsObject.lookToTheFuture)).strftime("%Y-%m-%d")

            # stocdata
            # try:
            #     # open
            #     thisrow.append(
            #         (MyStocks[thisStock][strtrainingdate]['open']/MyStocks[thisStock][strPredict_lookback]['open'])-1)
            # except Exception as e:
            #     thisrow.append(0)

            # try:
            #     # open
            #     thisrow.append(
            #         (MyStocks[thisStock][strtrainingdate]['high']/MyStocks[thisStock][strPredict_lookback]['high'])-1)
            # except Exception as e:
            #     thisrow.append(0)

            # try:
            #     # open
            #     thisrow.append(
            #         (MyStocks[thisStock][strtrainingdate]['low']/MyStocks[thisStock][strPredict_lookback]['open'])-1)
            # except Exception as e:
            #     thisrow.append(0)

            # try:
            #     if not strtrainingdate in MyStocks[thisStock]:
            #         MyStocks[thisStock][strtrainingdate] = {}

            #     thisrow.append(
            #         MyStocks[thisStock][strtrainingdate]['volume'])
            # except Exception as e:
            #     strtrainingdateyesterday = trainingdate - \
            #         timedelta(days=1)
            #     while strtrainingdateyesterday > SettingsObject.firstInculdedDate:
            #         if strtrainingdateyesterday.strftime("%Y-%m-%d") in MyStocks[thisStock]:
            #             if 'volume' in MyStocks[thisStock][strtrainingdateyesterday.strftime("%Y-%m-%d")]:
            #                 thisrow.append(
            #                     MyStocks[thisStock][strtrainingdateyesterday.strftime("%Y-%m-%d")]['volume'])
            #                 break
            #         strtrainingdateyesterday = strtrainingdateyesterday - \
            #             timedelta(days=1)
            #         if(strtrainingdateyesterday < SettingsObject.firstInculdedDate):
            #             raise Exception('No volume found backwards...')

            # try:
            #     # open
            #     thisrow.append(
            #         MyStocks[thisStock][strtrainingdate]['daydiff_volume'])
            # except Exception as e:
            #     strtrainingdateyesterday = trainingdate - \
            #         timedelta(days=1)
            #     while strtrainingdateyesterday > SettingsObject.firstInculdedDate:
            #         if strtrainingdateyesterday.strftime("%Y-%m-%d") in MyStocks[thisStock]:
            #             if 'volume' in MyStocks[thisStock][strtrainingdateyesterday.strftime("%Y-%m-%d")]:
            #                 thisrow.append(MyStocks[thisStock][strtrainingdateyesterday.strftime(
            #                     "%Y-%m-%d")]['daydiff_volume'])
            #                 break
            #         strtrainingdateyesterday = strtrainingdateyesterday - \
            #             timedelta(days=1)
            #         if(strtrainingdateyesterday < SettingsObject.firstInculdedDate):
            #             raise Exception(
            #                 'No daydiff_volume found backwards...')

            # try:
            #     # open
            #     thisrow.append(
            #         MyStocks[thisStock][strtrainingdate]['Rsi'])
            # except Exception as e:
            #     strtrainingdateyesterday = trainingdate - \
            #         timedelta(days=1)
            #     while strtrainingdateyesterday > SettingsObject.firstInculdedDate:
            #         if strtrainingdateyesterday.strftime("%Y-%m-%d") in MyStocks[thisStock]:
            #             if 'volume' in MyStocks[thisStock][strtrainingdateyesterday.strftime("%Y-%m-%d")]:
            #                 thisrow.append(
            #                     MyStocks[thisStock][strtrainingdateyesterday.strftime("%Y-%m-%d")]['Rsi'])
            #                 break
            #         strtrainingdateyesterday = strtrainingdateyesterday - \
            #             timedelta(days=1)
            #         if(strtrainingdateyesterday < SettingsObject.firstInculdedDate):
            #raise Exception("No Rsi found backwards...")

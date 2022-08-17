from typing import Match
from Api import *
#from MiscFunctions import *
from datetime import datetime, timezone, timedelta, tzinfo
import time
import pytz

import os
import json
import requests

from bs4 import BeautifulSoup
from dateutil.parser import parse
from datacollector.models import *

# GDC = GetDataClass
# GDC.GetCompanyList()
# GDC.GetAllStockHistory()
# GDC.getworldkpi()
# GDC.WriteDataForTraining()


class DataCrawler():
    def __init__(self):
        super(DataCrawler, self).__init__()
        self.settings = CollectorSettings.objects.first()
        if self.settings is None:
            CollectorSettings.objects.create(
                daysToInclude=365,
                RSIintervall=30,
                ValidStockdataLimit=70,
                avrageWindow=3
            )
        now = datetime.now().replace(tzinfo=pytz.utc)
        self.settings.firstInculdedDate = (datetime.now() - timedelta(
            days=self.settings.daysToInclude)).replace(tzinfo=pytz.utc)
        self.settings.lastIncudedDate = datetime.now().replace(tzinfo=pytz.utc)

    def utcformat(self, dt, timespec='milliseconds'):
        """convert datetime to string in UTC format (YYYY-mm-ddTHH:MM:SS.mmmZ)"""
        iso_str = dt.astimezone(timezone.utc).isoformat('T', timespec)
        return iso_str.replace('+00:00', 'Z')

    def parsetime(self, s):
        try:
            ret = parse(s)
        except ValueError:
            ret = datetime.utcfromtimestamp(s)
        except Exception as e:
            ret = datetime.fromtimestamp(s/1000, pytz.utc)
        return ret

    def getworldkpi(self):
        SettingsObject = Settings(True)

        if (os.path.exists(SettingsObject.KPIFile)):
            with open(SettingsObject.KPIFile) as MyKPIfile:
                WorldKPIJson = json.load(MyKPIfile)
        else:
            WorldKPIJson = {}
        getpage = requests.get('https://www.avanza.se/marknadsoversikt.html')
        soup = BeautifulSoup(getpage.text, 'html.parser')
        WorldKPIJson = {}
        nowsecstr = str(int(datetime.timestamp(
            datetime.now().replace(tzinfo=pytz.utc))))

        #Mydate = GetDataClass.parsetime(nowsecstr)
        #strsecondssinceepoch = str(int((Mydate - datetime(1970, 1, 1).replace(tzinfo=pytz.UTC)).totalseconds()*1000))

        for group in soup.findAll('optgroup'):
            WorldKPIJson[group.attrs['label']] = {}
            for opt in group.findAll('option'):
                customlabel = opt.text.replace(
                    '\r\n\t                               ', '')

                WorldKPIJson[group.attrs['label']][customlabel] = {}
                WorldKPIJson[group.attrs['label']
                             ][customlabel]['value'] = opt.attrs['value']

                subpage = requests.get(
                    'https://www.avanza.se/ab/component/indexperformance/marketoverview/' + opt.attrs['value'] + '?_=' + nowsecstr)
                subsoup = BeautifulSoup(subpage.text, 'html.parser')
                WorldKPIJson[group.attrs['label']
                             ][customlabel]['timeperiods'] = []
                for i in subsoup.find_all('li'):
                    datas = BeautifulSoup(str(i), 'html.parser')
                    for a in datas.find_all('a'):
                        WorldKPIJson[group.attrs['label']][customlabel]['timeperiods'].append(
                            a.attrs['data-timeperiod'])

                thisurl = 'https://www.avanza.se/ab/component/highstockchart/getchart/orderbook'
                thisbody = {
                    "orderbookId": WorldKPIJson[group.attrs['label']][customlabel]['value'],
                    "chartType": "AREA", "widthOfPlotContainer": 640,
                    "chartResolution": "DAY",
                    "navigator": "false",
                    "percentage": "false",
                    "volume": "false",
                    "owners": "false",
                    "start": GetDataClass.utcformat(SettingsObject.firstInculdedDate),
                    "end": GetDataClass.utcformat(datetime.now()),
                    "ta": []
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
                WorldKPIJson[group.attrs['label']][customlabel]['data'] = {}
                for index3, dataPoint in enumerate(data['dataPoints']):

                    mydate = datetime.fromtimestamp(
                        dataPoint[0]/1000, pytz.utc).date()
                    # mydate = mydate.replace(hour = 0, minute=0, tzinfo= pytz.utc) #sommaRTIDER

                    #StocksjsoninMemory[thiscompany][str(mydate)] = {}
                    if (dataPoint[1] != None):
                        WorldKPIJson[group.attrs['label']][customlabel]['data'][str(
                            mydate)] = dataPoint[1]
                        backcounter = 1
                        yesterday = mydate-timedelta(days=1)
                        Lastknownprice = -1
                        if len(WorldKPIJson[group.attrs['label']][customlabel]['data']) > 1:
                            while not str(yesterday) in WorldKPIJson[group.attrs['label']][customlabel]['data']:
                                if yesterday <= SettingsObject.firstInculdedDate.date():
                                    Lastknownprice = 0
                                    break
                                yesterday = yesterday-timedelta(days=1)
                                backcounter += 1

                            if(Lastknownprice != 0):
                                Lastknownprice = WorldKPIJson[group.attrs['label']][customlabel]['data'][str(
                                    yesterday)]

                            AvrageChange = (WorldKPIJson[group.attrs['label']][customlabel]['data'][str(
                                mydate)] - Lastknownprice)/backcounter

                            dayAfter = yesterday + timedelta(days=1)
                            while not str(dayAfter) in WorldKPIJson[group.attrs['label']][customlabel]['data']:

                                WorldKPIJson[group.attrs['label']][customlabel]['data'][str(
                                    dayAfter)] = WorldKPIJson[group.attrs['label']][customlabel]['data'][str(dayAfter - timedelta(days=1))] + AvrageChange
                                dayAfter = dayAfter + timedelta(days=1)
                        else:
                            WorldKPIJson[group.attrs['label']
                                         ][customlabel]['data'][str(mydate)] = -1
                    else:
                        WorldKPIJson[group.attrs['label']
                                     ][customlabel]['data'][str(mydate)] = -1

                print(f'Group: {group} option: {customlabel} done')
            time.sleep(3)
        if (os.path.exists(SettingsObject.KPIFile)):
            os.remove(SettingsObject.KPIFile)
        OverWriteJson(SettingsObject.KPIFile, WorldKPIJson)

    def GetCompanyList(self):

        MyCompanys = {}

        MyCompanysReturned = {'Start': 'start'}
        LastcompanyId = -1

        MyCompanysCounter = -1
        NumberofComapnys = 0

        print("Starting Comapany Collection.....")

        kpisValuesIndex = {
            'onedaydiff': 1,
            'oneyearddiff': 2,
            'directavkastning': 3,
            # Direktavkastning är ett bolags aktieutdelning i förhållande till aktiekursen och ett mått på avkastningen till aktieägarna. Snittet för direktavkastning brukar ligga mellan 2,7 % - 4,1 %. Direktavkastningen räknas genom: (Utdelning per Aktie / Aktiekurs)
            'PE': 4,
            # P/E- tal står för 'Price/Earnings' vilket betyder Aktiekurs/Vinst. Nyckeltalet används när man ska bedöma aktiens värdering i förhållande till företagets vinst och ett P/E - tal på 10 betyder att man betalar 10 gånger årsvinsten för en aktie. Snittet för P/E-tal brukar ligga mellan 12 - 16 och räknas genom: (Aktiekurs / Vinst Per Aktie )
            'PS': 5,
            # P/S står för 'Price/Sales' vilket betyder Aktiekurs/Omsättning. Nyckeltalet används när man ska bedöma hur mycket varje omsättningskrona värderas i förhållande till aktiekursen. Snittet för P/S-tal brukar ligga mellan 0,9 - 3,1 och varierar kraftigt beroende på omsättningens lönsamhet. P/S räknas genom: (Aktiekurs/Omsättning Per Aktie)
            'PB': 6,
            # P/B- tal står för 'Price/Bookvalue' vilket betyder Aktiekurs/eget kapital. Nyckeltalet används till att visa hur företagets eget kapital värderas i relation till aktiekursen. Snittet för P/B-tal brukar ligga mellan 1,4 - 2,4 och varierar kraftigt beroende på hur kapitalintensivt företaget är och tillgångarnas lönsamhet. (Aktiekurs/Eget Kapital Per Aktie)
            'kpitime': 7,  # Time-part
            'kpidate': 8,  # Date-part
            # The date the Kpis were valid

        }

        while (MyCompanysReturned != ""):
            MyCompanysCounter = MyCompanysCounter + 1
            print(
                f'****************  Fetching company {MyCompanysCounter*100}-{(MyCompanysCounter+1)*100} *************')
            MyCompanysReturned = GetPatComapnyPage(MyCompanysCounter)
            TotalFilteredComapnys = MyCompanysReturned['totalFiltered']
            TotalCompanys = MyCompanysReturned['total']
            MyCompanysReturned = MyCompanysReturned['data']
            try:
                if (len(MyCompanysReturned) == 0):
                    break
                elif (MyCompanysReturned[0]["companyId"] == LastcompanyId):
                    break
                else:
                    LastcompanyId = MyCompanysReturned[0]["companyId"]
            except Exception as e:
                print(f'Exception: {e}')
                break
            for company in MyCompanysReturned:
                NumberofComapnys = NumberofComapnys + 1
                if(company['name'].lower() not in MyCompanys):
                    MyCompanys[company['name'].lower()] = {}
                try:
                    MyCompanys[company['name'].lower(
                    )]['companyId'] = company['companyId']
                    MyCompanys[company['name'].lower(
                    )]['countryId'] = company['countryId']
                    MyCompanys[company['name'].lower(
                    )]['marketId'] = company['marketId']
                    MyCompanys[company['name'].lower(
                    )]['sectorId'] = company['sectorId']
                    MyCompanys[company['name'].lower(
                    )]['branchId'] = company['branchId']
                    MyCompanys[company['name'].lower(
                    )]['countryUrlName'] = company['countryUrlName'].lower()
                    MyCompanys[company['name'].lower(
                    )]['shortName'] = company['shortName']

                except Exception as e:
                    print(e)
                    continue

            print(f'***** {(NumberofComapnys/TotalFilteredComapnys)*100}% of {TotalFilteredComapnys} comapnys fetched. Totally there is {TotalCompanys} online..')

        for company in MyCompanys:
            try:
                thisCompany = Companies.objects.get_or_create(
                    name=company,
                    companyId=MyCompanys[company]['companyId'],
                    countryId=MyCompanys[company]['countryId'],
                    marketId=MyCompanys[company]['marketId'],
                    sectorId=MyCompanys[company]['sectorId'],
                    branchId=MyCompanys[company]['branchId'],
                    countryUrlName=MyCompanys[company]['countryUrlName'],
                    shortName=MyCompanys[company]['shortName'],
                )
            except Exception as e:
                print(e)

    def GetAllStockHistory(self):

        Grandstart = time.time()
        StocksjsoninMemory = {}
        companysectorbrachsummery = {}

        MyCompanys = Companies.objects.all()

        TotalNumberOfCompanies = MyCompanys.count()

        if TotalNumberOfCompanies > 0:
            Counter = 0

            for indexstart, thiscompany in enumerate(MyCompanys):
                CompanyRDIIntervall = []
                if not thiscompany.name in StocksjsoninMemory:
                    StocksjsoninMemory[thiscompany.name] = {}
                StocksjsoninMemory[thiscompany.name]['UsableData'] = False
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

                    print(f'looking at {thiscompany.name}', end='\r')
                    Missingdiffs = 0
                    #smallstart = time.time()
                    Counter += 1
                    from_string = str(
                        int(datetime.timestamp(self.settings.firstInculdedDate)))
                    to_string = str(
                        int(datetime.timestamp(self.settings.lastIncudedDate)))

                    History = GetPatComapnyHistory(
                        thiscompany.shortName, from_string, to_string, self.settings.daysToInclude)
                    if(len(History['t']) < self.settings.daysToInclude):
                        print('', end='\r')
                        print(
                            f'looking at {thiscompany.name} ...To little data')
                        continue

                    removedstocklencounter = 0

                    Created = 1
                    totalpoints = 1

                    for index, datepoint in enumerate(History['t']):
                        totalpoints += 1
                        mydate = datetime.fromtimestamp(
                            datepoint, pytz.utc)
                        # mydate = mydate.replace(hour = 0, minute=0, tzinfo= pytz.utc) #sommaRTIDER

                        if(index == 0):  # first
                            # earliest stockdate to late
                            if(mydate > self.settings.firstInculdedDate):
                                print('', end='\r')
                                print(
                                    'looking at {thiscompany.name} ...to late first date')
                                break

                        StocksjsoninMemory[thiscompany.name][str(mydate)] = {}
                        StocksjsoninMemory[thiscompany.name][str(
                            mydate)]['open'] = History['o'][index]
                        StocksjsoninMemory[thiscompany.name][str(
                            mydate)]['close'] = History['c'][index]
                        StocksjsoninMemory[thiscompany.name][str(
                            mydate)]['high'] = History['h'][index]
                        StocksjsoninMemory[thiscompany.name][str(
                            mydate)]['low'] = History['l'][index]
                        StocksjsoninMemory[thiscompany.name][str(
                            mydate)]['volume'] = History['v'][index]
                        Histotycounter = 0
                        while(History['v'][index] == 0):
                            History['v'][index] = History['v'][index -
                                                               1 - Histotycounter]
                            Histotycounter = Histotycounter - 1

                        StocksjsoninMemory[thiscompany.name][str(mydate)]['daydiff_volume'] = (
                            History['o'][index] - History['c'][index])/History['v'][index]

                        CompanyRDIIntervall.append(
                            StocksjsoninMemory[thiscompany.name][str(mydate)]['close'])

                        while (len(CompanyRDIIntervall) > self.settings.RSIintervall):
                            CompanyRDIIntervall.pop(0)
                        ups = 1
                        downs = 1
                        if len(CompanyRDIIntervall) == self.settings.RSIintervall:
                            for day in range(len(CompanyRDIIntervall)-1):
                                if day > 0:
                                    RDItoday = CompanyRDIIntervall[day] / \
                                        CompanyRDIIntervall[day-1]
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

                        rs = ups/downs
                        rsi = 100-(100/(1 + rs))
                        StocksjsoninMemory[thiscompany.name][str(
                            mydate)]['Rsi'] = rsi

                        if len(StocksjsoninMemory[thiscompany.name]) > 2:

                            backcounter = 1
                            yesterday = mydate-timedelta(days=1)
                            while not str(yesterday) in StocksjsoninMemory[thiscompany.name]:

                                yesterday = yesterday-timedelta(days=1)
                                backcounter += 1

                            Lastknownprice = StocksjsoninMemory[thiscompany.name][str(
                                yesterday)]['close']
                            AvrageChange = (StocksjsoninMemory[thiscompany.name][str(
                                mydate)]['close'] - Lastknownprice)/backcounter

                            dayAfter = yesterday + timedelta(days=1)
                            while not str(dayAfter) in StocksjsoninMemory[thiscompany.name]:

                                StocksjsoninMemory[thiscompany.name][str(dayAfter)] = {
                                }
                                StocksjsoninMemory[thiscompany.name][str(dayAfter)]['close'] = StocksjsoninMemory[thiscompany.name][str(
                                    dayAfter - timedelta(days=1))]['close'] + AvrageChange
                                StocksjsoninMemory[thiscompany.name][str(dayAfter)]['Rsi'] = StocksjsoninMemory[thiscompany.name][str(
                                    dayAfter - timedelta(days=1))]['Rsi']
                                StocksjsoninMemory[thiscompany.name][str(dayAfter)]['open'] = StocksjsoninMemory[thiscompany.name][str(
                                    dayAfter - timedelta(days=1))]['open']
                                StocksjsoninMemory[thiscompany.name][str(dayAfter)]['high'] = StocksjsoninMemory[thiscompany.name][str(
                                    dayAfter - timedelta(days=1))]['high']
                                StocksjsoninMemory[thiscompany.name][str(dayAfter)]['low'] = StocksjsoninMemory[thiscompany.name][str(
                                    dayAfter - timedelta(days=1))]['low']
                                StocksjsoninMemory[thiscompany.name][str(dayAfter)]['volume'] = StocksjsoninMemory[thiscompany.name][str(
                                    dayAfter - timedelta(days=1))]['volume']
                                StocksjsoninMemory[thiscompany.name][str(dayAfter)]['daydiff_volume'] = StocksjsoninMemory[thiscompany.name][str(
                                    dayAfter - timedelta(days=1))]['daydiff_volume']
                                dayAfter = dayAfter + timedelta(days=1)

                    totallemn = index-removedstocklencounter
                    RatioDataCreated = (Created/totallemn)*100
                    UsableData = False
                    if (RatioDataCreated <= self.settings.ValidStockdataLimit):
                        UsableData = True
                    StocksjsoninMemory[thiscompany.name]['UsableData'] = UsableData
                except Exception as e:
                    print(e)
                    print(
                        f'at {index} in {thiscompany.name}, removed from StocksjsoninMemory')

                    StocksjsoninMemory.pop(thiscompany.name, None)
                    continue

                SmallEnd = time.time()
                ELAPSED = SmallEnd-Grandstart
                AVRAGE = ELAPSED/Counter
                ETA = (TotalNumberOfCompanies-Counter)*(ELAPSED/Counter)
                PROGRESS = (Counter/TotalNumberOfCompanies)*100

                print(
                    f'****************                            StockDownloaded                     ************************')
                print(
                    f'*   Company: {thiscompany.name}                                                              ')
                print(
                    f'*   Elapsed time: {ELAPSED}s with an avrage time per loop:{AVRAGE}s                                     ')
                print(
                    f'*   MissingDiffs: {Missingdiffs}                                                                        ')
                print(
                    f'*   Created: {RatioDataCreated}%, Valid data: {UsableData}                                                           ')
                print(
                    f'*   {PROGRESS}% done giving an ETA in {ETA}s                                                            ')
                print(
                    f'*                                                                                                       ')
                print(
                    f'****************                           *********                            ************************')
                print(f' ')
                print(f' ')

            # print(f'Writing company sector branch to disk......')
            # if (os.path.exists(SettingsObject.CompanysecbraFile)):
            #     os.remove(SettingsObject.CompanysecbraFile)
            # OverWriteJson(SettingsObject.CompanysecbraFile,
            #               companysectorbrachsummery)

            print(f'Writing stocksfile to disk......')
            # if (os.path.exists(SettingsObject.StocksFile)):
            #     os.remove(SettingsObject.StocksFile)
            # OverWriteJson(SettingsObject.StocksFile, StocksjsoninMemory)

            for index3, comapnystock in enumerate(StocksjsoninMemory):
                print(index3, ' writing stock to db... ', comapnystock)
                for datapointday in StocksjsoninMemory[comapnystock]:
                    # comapny = models.ForeignKey(Companies, on_delete=models.DO_NOTHING)
                    # timestamp = models.DateTimeField(default=None, blank=True)
                    # close = models.FloatField(default=-1)
                    # open = models.FloatField(default=-1)
                    # high = models.FloatField(default=-1)
                    # low = models.FloatField(default=-1)
                    # volume = models.FloatField(default=-1)
                    # daydiff_volume = models.FloatField(default=-1)
                    if datapointday != 'UsableData':
                        CompanyStockDay.objects.get_or_create(
                            comapny=Companies.objects.get(name=comapnystock),
                            timestamp=datapointday,
                            close=StocksjsoninMemory[comapnystock][datapointday]['close'],
                            open=StocksjsoninMemory[comapnystock][datapointday]['open'],
                            high=StocksjsoninMemory[comapnystock][datapointday]['high'],
                            low=StocksjsoninMemory[comapnystock][datapointday]['low'],
                            volume=StocksjsoninMemory[comapnystock][datapointday]['volume'],
                            daydiff_volume=StocksjsoninMemory[comapnystock][datapointday]['daydiff_volume'],
                        )

            print(f'Writing company_sector_brach_summery to disk')

    def WriteDataForTraining(self):
        SettingsObject = Settings(False)

        stocksJson = open(SettingsObject.StocksFile)
        MyStocks = json.load(stocksJson)

        KPIJson = open(SettingsObject.KPIFile)
        MyKPI = json.load(KPIJson)

        trainingdate = SettingsObject.firstInculdedDate

        if (os.path.exists(SettingsObject.TrainingData)):
            os.remove(SettingsObject.TrainingData)

        if (os.path.exists(SettingsObject.AnswerData)):
            os.remove(SettingsObject.AnswerData)

        if (os.path.exists(SettingsObject.Traininglog)):
            os.remove(SettingsObject.Traininglog)

        if (os.path.exists(SettingsObject.StockindexFile)):
            os.remove(SettingsObject.StockindexFile)

        if (os.path.exists(SettingsObject.Targetsfile)):
            os.remove(SettingsObject.Targetsfile)

        writetodisk([f'FirtsDate', trainingdate.strftime(
            "%Y-%m-%d"),  '',  ''], SettingsObject.Traininglog)
        writetodisk([f'SettingsObject.lookToTheFuture', (trainingdate + timedelta(
            days=SettingsObject.lookToTheFuture)).strftime("%Y-%m-%d"),  '',  ''], SettingsObject.Traininglog)
        daycounter = 0
        Stockindexjson = {}
        while trainingdate <= SettingsObject.lastIncudedDate:

            thisrow = []
            strtrainingdateyester = (
                trainingdate-timedelta(days=1)).strftime("%Y-%m-%d")
            daycounter = daycounter + 1
            SettingsObject.KPIwidth = 0
            for index, thisKPI in enumerate(MyKPI):

                for index2, thisSubKPI in enumerate(MyKPI[thisKPI]):
                    try:
                        thisrow.append(
                            MyKPI[thisKPI][thisSubKPI]['data'][str(trainingdate)])
                        # print(MyKPI[thisKPI][thisSubKPI]['data'][str(trainingdate)])
                        if (daycounter == 1):
                            SettingsObject.KPIwidth = SettingsObject.KPIwidth + 1
                            SettingsObject.firstkpiday = str(trainingdate)

                    except Exception as e:
                        if (daycounter > SettingsObject.lookToTheFuture):
                            trainingdateyesterday = trainingdate - \
                                timedelta(days=1)
                            while not trainingdateyesterday.strftime("%Y-%m-%d") in MyKPI[thisKPI][thisSubKPI]['data']:

                                if(trainingdateyesterday < SettingsObject.firstInculdedDate):
                                    MyKPI[thisKPI][thisSubKPI]['data'][trainingdateyesterday.strftime(
                                        "%Y-%m-%d")] = 0
                                    break
                                trainingdateyesterday = trainingdateyesterday - \
                                    timedelta(days=1)
                            thisrow.append(
                                MyKPI[thisKPI][thisSubKPI]['data'][trainingdateyesterday.strftime("%Y-%m-%d")])
                        else:
                            thisrow.append(0)

                        if (daycounter == 1):
                            SettingsObject.KPIwidth = SettingsObject.KPIwidth + 1
                            SettingsObject.firstkpiday = str(trainingdate)

            if (daycounter == 1):
                SettingsObject.save()
            strtrainingdate = trainingdate.strftime("%Y-%m-%d")
            strPredict_lookback = (
                trainingdate - timedelta(days=SettingsObject.lookToTheFuture)).strftime("%Y-%m-%d")
            strprediction = (
                trainingdate + timedelta(days=SettingsObject.lookToTheFuture)).strftime("%Y-%m-%d")

            for thisStock in MyStocks:
                if(MyStocks[thisStock]['UsableData'] == False):
                    continue
                try:
                    # relative
                    try:
                        # close

                        thisrow.append(
                            (MyStocks[thisStock][strtrainingdate]['close']/MyStocks[thisStock][strPredict_lookback]['close'])-1)
                        if (daycounter == 1):
                            Stockindexjson[thisStock] = len(thisrow)-1
                    except Exception as e:
                        thisrow.append(0)
                        if (daycounter == 1):
                            Stockindexjson[thisStock] = len(thisrow)-1

                    try:
                        # open
                        thisrow.append(
                            (MyStocks[thisStock][strtrainingdate]['open']/MyStocks[thisStock][strPredict_lookback]['open'])-1)
                    except Exception as e:
                        thisrow.append(0)

                    try:
                        # open
                        thisrow.append(
                            (MyStocks[thisStock][strtrainingdate]['high']/MyStocks[thisStock][strPredict_lookback]['high'])-1)
                    except Exception as e:
                        thisrow.append(0)

                    try:
                        # open
                        thisrow.append(
                            (MyStocks[thisStock][strtrainingdate]['low']/MyStocks[thisStock][strPredict_lookback]['open'])-1)
                    except Exception as e:
                        thisrow.append(0)

                    try:
                        if not strtrainingdate in MyStocks[thisStock]:
                            MyStocks[thisStock][strtrainingdate] = {}

                        thisrow.append(
                            MyStocks[thisStock][strtrainingdate]['volume'])
                    except Exception as e:
                        strtrainingdateyesterday = trainingdate - \
                            timedelta(days=1)
                        while strtrainingdateyesterday > SettingsObject.firstInculdedDate:
                            if strtrainingdateyesterday.strftime("%Y-%m-%d") in MyStocks[thisStock]:
                                if 'volume' in MyStocks[thisStock][strtrainingdateyesterday.strftime("%Y-%m-%d")]:
                                    thisrow.append(
                                        MyStocks[thisStock][strtrainingdateyesterday.strftime("%Y-%m-%d")]['volume'])
                                    break
                            strtrainingdateyesterday = strtrainingdateyesterday - \
                                timedelta(days=1)
                            if(strtrainingdateyesterday < SettingsObject.firstInculdedDate):
                                raise Exception('No volume found backwards...')

                    try:
                        # open
                        thisrow.append(
                            MyStocks[thisStock][strtrainingdate]['daydiff_volume'])
                    except Exception as e:
                        strtrainingdateyesterday = trainingdate - \
                            timedelta(days=1)
                        while strtrainingdateyesterday > SettingsObject.firstInculdedDate:
                            if strtrainingdateyesterday.strftime("%Y-%m-%d") in MyStocks[thisStock]:
                                if 'volume' in MyStocks[thisStock][strtrainingdateyesterday.strftime("%Y-%m-%d")]:
                                    thisrow.append(MyStocks[thisStock][strtrainingdateyesterday.strftime(
                                        "%Y-%m-%d")]['daydiff_volume'])
                                    break
                            strtrainingdateyesterday = strtrainingdateyesterday - \
                                timedelta(days=1)
                            if(strtrainingdateyesterday < SettingsObject.firstInculdedDate):
                                raise Exception(
                                    'No daydiff_volume found backwards...')

                    try:
                        # open
                        thisrow.append(
                            MyStocks[thisStock][strtrainingdate]['Rsi'])
                    except Exception as e:
                        strtrainingdateyesterday = trainingdate - \
                            timedelta(days=1)
                        while strtrainingdateyesterday > SettingsObject.firstInculdedDate:
                            if strtrainingdateyesterday.strftime("%Y-%m-%d") in MyStocks[thisStock]:
                                if 'volume' in MyStocks[thisStock][strtrainingdateyesterday.strftime("%Y-%m-%d")]:
                                    thisrow.append(
                                        MyStocks[thisStock][strtrainingdateyesterday.strftime("%Y-%m-%d")]['Rsi'])
                                    break
                            strtrainingdateyesterday = strtrainingdateyesterday - \
                                timedelta(days=1)
                            if(strtrainingdateyesterday < SettingsObject.firstInculdedDate):
                                raise Exception('No Rsi found backwards...')

                except Exception as e:
                    print(f'Error: for {thisStock} , {e}')
                    writetodisk([f'StockError', str(
                        trainingdate),  f'{thisStock}',  f'{e}'], SettingsObject.Traininglog)
                    raise Exception(e)

            try:
                if (daycounter == 1):
                    OverWriteJson(SettingsObject.StockindexFile,
                                  Stockindexjson)

                print(f'{trainingdate} : {len(thisrow)} : {thisrow[0:10]}..')

                writetodisk(thisrow, SettingsObject.TrainingData)
                if(trainingdate.strftime("%Y-%m-%d") == '2021-11-17'):
                    v = 4
                #writetodisk(thisAnswerRow, SettingsObject.AnswerData)
                writetodisk([f'Date done:', str(
                    trainingdate),  f'Predictiondate: {strprediction}',  f'OK'], SettingsObject.Traininglog)
            except Exception as e:
                raise Exception(f'Something wrong: {e}')

            trainingdate = trainingdate + timedelta(days=1)

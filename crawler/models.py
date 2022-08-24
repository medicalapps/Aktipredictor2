from operator import mod
from django.db import models
from datetime import datetime

# Create your models here.
class Companies(models.Model):
    name = models.CharField(max_length=127, default='')
    companyId = models.IntegerField(default=-1)
    countryId = models.IntegerField(default=-1)
    marketId = models.IntegerField(default=-1)
    sectorId = models.IntegerField(default=-1)
    branchId = models.IntegerField(default=-1)
    countryUrlName = models.CharField(max_length=127, default='NOURL')
    shortName = models.CharField(max_length=127, default='NOSHORTNAME')
    corruptData = models.BooleanField(default=False)


class CompanyStockDay(models.Model):
    comapny = models.ForeignKey(Companies, on_delete=models.DO_NOTHING)
    timestamp = models.DateTimeField(default=None, blank=True)
    close = models.FloatField(default=-1)
    open = models.FloatField(default=-1)
    high = models.FloatField(default=-1)
    low = models.FloatField(default=-1)
    volume = models.FloatField(default=-1)
    daydiff_volume = models.FloatField(default=-1)


class WorldKPI(models.Model):
    group = models.CharField(max_length=127, default='NONAME')
    name = models.CharField(max_length=127, default='NONAME')
    timestamp = models.DateTimeField(default=None, blank=True)
    value = models.FloatField(default=-1)


class CollectorSettings(models.Model):
    registerName = models.CharField(max_length=127, default='Unnamed')
    daysToCollect = models.IntegerField(default=7)
    RSIintervall = models.IntegerField(default=-1)
    ValidStockdataLimit = models.IntegerField(default=-1)
    avrageWindow = models.IntegerField(default=-1)
    firstInculdedDate = models.DateTimeField(
        default=datetime.now(), blank=True)
    lastIncudedDate = models.DateTimeField(
        default=datetime.now(), blank=True)
    comapnys = models.ManyToManyField(Companies, blank=True, related_name='CollectedCompanies')
    worldKPIs = models.ManyToManyField(WorldKPI, blank=True, related_name='CollectedCKPI')
    timestamp = models.DateTimeField(auto_now=True)
    fileName = models.CharField(max_length=127, default='NONAME')
    


# {
#     "lastkpiindex": 68,
#     "firstkpiday": "2019-02-18",
#     "firsttrainingday": "2019-02-18",
#     "RequestPayload" : {
#         "page":1,
#         "rowsInPage":100,
#         "nameFilter":"",
#         "kpiFilter":
#         [
#             {"kpiId":"7","calculation":"0","calcTime":"0","categoryId":11,"calculationType":3,"lowPrice":null,"highPrice":null},
#             {"kpiId":"151","calculation":"20","calcTime":"1","categoryId":9,"calculationType":2,"lowPrice":null,"highPrice":null},
#             {"kpiId":"151","calculation":"20","calcTime":"6","categoryId":9,"calculationType":2,"lowPrice":null,"highPrice":null},
#             {"kpiId":"1","calculation":"1","calcTime":"0","categoryId":0,"calculationType":2,"lowPrice":null,"highPrice":null},
#             {"kpiId":"2","calculation":"1","calcTime":"0","categoryId":0,"calculationType":2,"lowPrice":null,"highPrice":null},
#             {"kpiId":"3","calculation":"1","calcTime":"0","categoryId":0,"calculationType":2,"lowPrice":null,"highPrice":null},
#             {"kpiId":"4","calculation":"1","calcTime":"0","categoryId":0,"calculationType":2,"lowPrice":null,"highPrice":null},
#             {"kpiId":"12","calculation":"0","calcTime":"0","categoryId":11,"calculationType":3,"lowPrice":null,"highPrice":null},
#             {"kpiId":"2","calculation":"0","calcTime":"0","categoryId":11,"calculationType":3,"lowPrice":null,"highPrice":null},
#             {"kpiId":"1","calculation":"0","calcTime":"0","categoryId":11,"calculationType":3,"lowPrice":null,"highPrice":null},
#             {"kpiId":"5","calculation":"0","calcTime":"0","categoryId":11,"calculationType":3,"lowPrice":null,"highPrice":null}
#         ],
#         "watchlistId":null,
#         "selectedCountries":[1,2,3,4],
#         "companyNameOrdering":0
#     },


#     "SectorBranch" : {
#     "Energi":
#     {
#         "ID":3,
#         "Brancher":{
#             "OljaGasBorrning":1,
#             "OljaGasExploatering":2,
#             "OljaGasTransport":3,
#             "OljaGasForsealjning":4,
#             "OljaGasService":5,
#             "BreansleKol":6,
#             "BreansleUran":7
#         }
#     },
#     "Kraftforsorjning":
#     {
#         "ID":10,
#         "Brancher":
#         {
#             "Elforsorjning":8,
#             "Gasforsorjning":9,
#             "Vattenforsorjning":10,
#             "Fornybarenergi":11,
#             "Vindkraft":12,
#             "Solkraft":13,
#             "Bioenergi":14
#         }
#     },
#     "Material":
#     {
#         "ID":7,
#         "Brancher":
#         {
#             "Kemikalier":15,
#             "GruvProspektDrift":16,
#             "GruvIndustrimetaller":17,
#             "GruvGuldSilver":18,
#             "Gruveadelstenar":19,
#             "GruvService":20,
#             "Skogsbolag":21,
#             "Forpackning":22
#         }
#     },
#     "Dagligvaror":
#     {
#         "ID":2,
#         "Brancher":
#         {
#             "Drycker":58,
#             "Jordbruk":59,
#             "Fiskodling":60,
#             "Tobak":61,
#             "Livsmedel":62,
#             "Hygienprodukter":63,
#             "Healsoprodukter":64,
#             "Apotek":65,
#             "Livsmedelsbutiker":66
#         }
#     },
#     "Seallankopsvaror":
#     {
#         "ID":8,
#         "Brancher":
#         {
#             "KleaderSkor":43,
#             "Accessoarer":44,
#             "Hemelektronik":45,
#             "MoblerInredning":46,
#             "FritidSport":47,
#             "BilMotor":48,
#             "Konsumentservice":49,
#             "Detaljhandel":50,
#             "HotellCamping":51,
#             "RestaurangCafe":52,
#             "ResorNojen":53,
#             "BettingCasino":54,
#             "GamingSpel":55,
#             "Marknadsforing":56,
#             "MediaPublicering":57
#         }
#     },
#     "Industri":
#     {
#         "ID":5,
#         "Brancher":
#         {
#             "Industrimaskiner":23,
#             "Industrikomponenter":24,
#             "ElektroniskaKomponenter":25,
#             "MilitearForsvar":26,
#             "Energiatervinning":27,
#             "ByggnationInfrastruktur":28,
#             "Bostadsbyggnation":29,
#             "InstallationVVS":30,
#             "Byggmaterial":31,
#             "Bygginredning":32,
#             "Bemanning":33,
#             "Affearskonsulter":34,
#             "Seakerhet":35,
#             "Utbildning":36,
#             "StodtjeansterService":37,
#             "MeatningAnalys":38,
#             "InformationData":39,
#             "Flygtransport":40,
#             "SjofartRederi":41,
#             "TagLastbilstransport":42
#         }
#     },
#     "Healsovard":
#     {
#         "ID":4,
#         "Brancher":
#         {
#             "Leakemedel":77,
#             "Biotech":78,
#             "MedicinskUtrustning":79,
#             "HealsovardHjealpmedel":80,
#             "SjukhusVardhem":81
#         }

#     },
#     "FinansFastighet":
#     {
#         "ID":1,
#         "Brancher":
#         {
#             "Banker":68,
#             "Nischbanker":69,
#             "KreditFinansiering":70,
#             "Kapitalforvaltning":71,
#             "Fondforvaltning":72,
#             "Investmentbolag":73,
#             "Forseakring":74,
#             "Fastighetsbolag":75,
#             "FastighetREIT":76
#         }

#     },
#     "Informationsteknik":
#     {
#         "ID":6,
#         "Brancher":
#         {
#             "ElektronikTillverkning":82,
#             "DatorerHardvara":83,
#             "ElektroniskUtrustning":84,
#             "Biometri":85,
#             "Kommunikation":86,
#             "RymdSatellitteknik":87,
#             "SeakerhetBevakning":88,
#             "ITKonsulter":89,
#             "AffearsITSystem":90,
#             "Internettjeanster":91,
#             "BetalningEhandel":92
#         }

#     },
#     "Telekommunikation":
#     {
#         "ID":9,
#         "Brancher":
#         {
#             "BredbandTelefoni":93,
#             "Telekomtjeanster":94
#         }

#     }
#     },

#     "CompanysFile" :"Data/Companys.json",

#     "StocksFile" :"Data/Stocks.json",

#     "CompanysecbraFile" :"Data/CompanysecbraFile.json",

#     "StockindexFile" :"Data/StockindexFile.json",

#     "TrainingData" :"Data/TrainingData.csv",

#     "TrueAnswersfile" :"Data/TrueAnswers.csv",

#     "PredictionAnswersfile" :"Data/PredictionAnswers.csv",

#     "TrainingAnswersfile" :"Data/TrainingAnswersfile.csv",

#     "KPIFile" :"Data/KPI.json",


#     "AnswerData" :"Data/AnswerData.csv",

#     "Traininglog" :"Data/TrainingLog.csv",

#     "Targetsfile" :"Data/CompanyTargets.json",

#     "ModelPath" :"Data/model/",

#     "Lossfile" : "Data/Accuracy.csv",

#     "trainingdifffile" :"Data/TrainingDiff.csv",

#     "validationdifffile" :"Data/ValidationDiff.csv",

#     "Currentsettings" :"Data/CurrentSettings.json",

#     "CompanyHeader" :["companyId", "name", "countryId", "marketId", "sectorId", "branchId", "countryUrlName"],

#     "UseMockData" : false,


#     "diffs" :[1,3,7,14,28,70,140],


#     "TrainingPart" :0.9,
#     "TargetStockindexarray" :[],
#     "TargetStocknamearray" :[],
#     "ValidStockdataLimit" :50,
#     "stockTrainingTime" :15,
#     "avrageWindow" :3,
#     "currentsector" :"7",
#     "currentbranch" :"16",
#     "lr" :0.005,
#     "RSIintervall" :30,
#     "lookToTheFuture" :3,
#     "trainingDataWindow" :30,

#     "KPIwidth" : 0,


#     "inspecting" : false,
#     "YearsToInclude" : 2,

#     "weightlimit_high" : 0.2,
#     "weightlimit_low" : -0.2,
#     "bias_high" : 0.2,
#     "bias_low" : -0.2


# }

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
    collectionName = models.CharField(max_length=127, default='')
    daysToCollect = models.IntegerField(default=7)
    RSIintervall = models.IntegerField(default=-1)
    ValidStockdataLimit = models.IntegerField(default=-1)
    avrageWindow = models.IntegerField(default=-1)
    firstInculdedDate = models.DateTimeField(default=datetime.now(), blank=True)
    lastIncudedDate = models.DateTimeField(default=datetime.now(), blank=True)
    comapnys = models.ManyToManyField(Companies, blank=True, related_name='CollectedCompanies')
    worldKPIs = models.ManyToManyField(WorldKPI, blank=True, related_name='CollectedCKPI')
    timestamp = models.DateTimeField(auto_now=True)
    collectionTimestamp = models.DateTimeField(auto_now=True)
    fileName = models.CharField(max_length=127, default='')
    completeCollection = models.BooleanField(default=False)
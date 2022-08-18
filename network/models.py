from django.db import models

# Create your models here.



class NetworkSettings(models.Model):

    trainingDataWindow = models.IntegerField(default=-1)
    
    weightlimit_low
    weightlimit_high
    bias_low
    bias_high
    PredictionPart
    ???lookToTheFuture
    stockTrainingTime
    ModelPath
    lr
    RSIintervall = models.IntegerField(default=-1)
    ValidStockdataLimit = models.IntegerField(default=-1)
    avrageWindow = models.IntegerField(default=-1)
    firstInculdedDate = models.DateTimeField(
        default=datetime.now(), blank=True)
    lastIncudedDate = models.DateTimeField(
        default=datetime.now(), blank=True)

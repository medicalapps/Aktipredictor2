from django.db import models
from crawler.models import Companies, WorldKPI
from django.contrib.postgres.fields import ArrayField

# Create your models here.
    
class Network(models.Model):
    networkName = models.CharField(max_length=127, default='NONAME')
    trainingDataWindow = models.IntegerField(default=5)
    reSeed = models.BooleanField(default=False)
    weightLimitLow = models.FloatField(default=-0.1)
    weightLimitHigh = models.FloatField(default=0.1)
    biasLow = models.FloatField(default=0.1)
    biasHigh = models.FloatField(default=-1)
    predictionPart = models.FloatField(default=0.2)
    stockTrainingTime = models.IntegerField(default=60)
    modelPath = models.CharField(max_length=127, default='', blank=True)
    lR = models.FloatField(default=0.01)
    mockData = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True)
    targets  = models.ManyToManyField(Companies, blank=True, related_name='MyTargets')
    predictingDays = models.IntegerField(default=-1)
    inputDim = ArrayField( models.IntegerField(default=-1))
    hidden_dim = models.IntegerField(default=-1)
    output_dim = ArrayField( models.IntegerField(default=-1))
    n_layers = models.IntegerField(default=-1)
    batchsize = models.IntegerField(default=-1)
    drop_prob= models.FloatField(default=0.01)
        

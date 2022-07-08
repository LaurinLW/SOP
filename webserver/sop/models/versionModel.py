from django.db import models
from .resultModel import ResultModel
from .algorithmModel import AlgorithmModel
from .experimentModel import ExperimentModel

class VersionModel(models.Model):
    """ This class is the supclass of the Model-class from Django.
        It contains the essentail fields and data that is stored in the database.
    """ 
    parameterSettings = models.JSONField()
    version = models.CharField(max_length=50)
    seed = models.IntegerField()
    minDimension = models.IntegerField()
    maxDimension = models.IntegerField()
    progress = models.IntegerField()
    pid = models.IntegerField()
    results = models.ForeignKey(ResultModel, on_delete=models.CASCADE)
    algorithms = models.ManyToManyField(AlgorithmModel)
    experiment = models.ForeignKey(ExperimentModel, on_delete=models.CASCADE)
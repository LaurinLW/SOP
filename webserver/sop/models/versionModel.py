from django.db import models
from .algorithmModel import AlgorithmModel
from .experimentModel import ExperimentModel


class VersionModel(models.Model):
    """ This class is the supclass of the Model-class from Django.
        It contains the essentail fields and data that is stored in the database.
    """
    parameterSettings = models.JSONField(null=True)
    edits = models.IntegerField()
    runs = models.IntegerField()
    seed = models.IntegerField()
    status = models.CharField(max_length=20)
    numberSubspaces = models.IntegerField()
    minDimension = models.IntegerField()
    maxDimension = models.IntegerField()
    progress = models.IntegerField()
    pid = models.CharField(max_length=10, null=True)
    algorithms = models.ManyToManyField(AlgorithmModel)
    experiment = models.ForeignKey(ExperimentModel, on_delete=models.CASCADE)
    error = models.CharField(max_length=100, null=True)

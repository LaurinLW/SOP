from django.db import models
from django.contrib.auth.models import User
from .datasetModel import DatasetModel


class ExperimentModel(models.Model):
    """ This class is the supclass of the Model-class from Django.
        It contains the essentail fields and data that is stored in the database.
    """
    name = models.CharField(max_length=50)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    dataset = models.ForeignKey(DatasetModel, on_delete=models.CASCADE, null=True)
    latestVersion = models.CharField(max_length=20)
    latestStatus = models.CharField(max_length=20)

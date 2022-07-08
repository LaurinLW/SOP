from django.db import models
from .datasetModel import DatasetModel

class SubspaceModel(models.Model):
    """ This class is the supclass of the Model-class from Django.
        It contains the essentail fields and data that is stored in the database.
    """ 
    pickedColumns = models.JSONField()
    dataset = models.ForeignKey(DatasetModel, on_delete=models.CASCADE)
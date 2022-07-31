from django.db import models
from .subspaceModel import SubspaceModel
from .versionModel import VersionModel


class ResultModel(models.Model):
    """ This class is the supclass of the Model-class from Django.
        It contains the essentail fields and data that is stored in the database.
    """
    resultFile = models.FileField()
    subspace = models.ForeignKey(SubspaceModel, on_delete=models.CASCADE, null=True)
    version = models.ForeignKey(VersionModel, on_delete=models.CASCADE)

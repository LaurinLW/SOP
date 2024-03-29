from django.db import models
from django.contrib.auth.models import User


class DatasetModel(models.Model):
    """ This class is the supclass of the Model-class from Django.
        It contains the essentail fields and data that is stored in the database.
    """
    name = models.CharField(max_length=50)
    file = models.FileField(upload_to='sop/views/user_datasets/')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

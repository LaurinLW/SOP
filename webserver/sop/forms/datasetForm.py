from django import forms
from models.datasetModel import DatasetModel


class DatasetForm(forms.ModelForm):
    """ This class is the subclass of the ModelForm.
        This form has the purpose to create a new dataset
    """
    class Meta:
        """ The Meta class contains the Meta-information about the Form
        """
        model = DatasetModel
        forms = ("name", "file")

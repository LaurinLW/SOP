from django import forms
from models.experimentModel import ExperimentModel


class ExperimentForm(forms.ModelForm):
    """ This class is the subclass of the ModelForm.
        This form has the purpose to create a new experiment
    """
    class Meta:
        """ The Meta class contains the Meta-information about the Form
        """
        model = ExperimentModel
        forms = ("name", "dataset")

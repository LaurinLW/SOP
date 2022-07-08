from django import forms
from models.algorithmModel import AlgorithmModel


class AlgorithmForm(forms.ModelForm):
    """ This class is the subclass of the ModelForm.
        This form has the purpose to create a new algorithm
    """
    class Meta:
        """ The Meta class contains the Meta-information about the Form
        """
        model = AlgorithmModel
        forms = ("name", "category", "file")

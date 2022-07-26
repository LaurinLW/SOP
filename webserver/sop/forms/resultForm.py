from django import forms
from ..models.resultModel import ResultModel


class ResultForm(forms.ModelForm):
    """ This class is the subclass of the ModelForm.
        This form has the purpose to create a new result
    """
    class Meta:
        """ The Meta class contains the Meta-information about the Form
        """
        model = ResultModel
        fields = ()

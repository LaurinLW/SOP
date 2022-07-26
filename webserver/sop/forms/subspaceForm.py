from django import forms
from ..models.subspaceModel import SubspaceModel


class SubspaceForm(forms.ModelForm):
    """ This class is the subclass of the ModelForm.
        This form has the purpose to create a new subspace
    """
    class Meta:
        """ The Meta class contains the Meta-information about the Form
        """
        model = SubspaceModel
        fields = ()

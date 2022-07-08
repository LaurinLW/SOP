from django import forms
from models.versionModel import VersionModel


class VersionForm(forms.ModelForm):
    """ This class is the subclass of the ModelForm.
        This form has the purpose to create a new Version
    """
    class Meta:
        """ The Meta class contains the Meta-information about the Form
        """
        model = VersionModel
        forms = ()

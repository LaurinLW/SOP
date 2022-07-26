from django import forms
from ..models.versionModel import VersionModel


class VersionForm(forms.ModelForm):
    """ This class is the subclass of the ModelForm.
        This form has the purpose to create a new Version
    """
    class Meta:
        """ The Meta class contains the Meta-information about the Form
        """
        model = VersionModel
        fields = ("seed", "minDimension", "maxDimension", "numberSubspaces")

    def save(self, commit=True):
        version = super(VersionForm, self).save(commit=False)
        version.experiment = self.experiment
        version.runs = 0
        version.edits = 1
        version.progress = 0
        version.status = "paused"
        if commit:
            version.save()
        return version

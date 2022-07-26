from django import forms
from ..models.experimentModel import ExperimentModel


class ExperimentForm(forms.ModelForm):
    """ This class is the subclass of the ModelForm.
        This form has the purpose to create a new experiment
    """
    class Meta:
        """ The Meta class contains the Meta-information about the Form
        """
        model = ExperimentModel
        fields = ("name",)

    def save(self, commit=True):
        experiment = super(ExperimentForm, self).save(commit=False)
        experiment.name = self.cleaned_data['name']
        experiment.creator = self.creator
        experiment.dataset = self.dataset
        experiment.latestVersion = "1.0"
        experiment.latestStatus = "paused"
        if commit:
            experiment.save()
        return experiment

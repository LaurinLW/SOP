from sop.models import ExperimentModel, VersionModel
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import redirect
from django.db.models import Q, Max


class ExperimentIterateView(View, LoginRequiredMixin):
    """ This class is a subclass of LoginRequiredMixin and View
    """

    def get(self, request, *args, **kwargs):
        """ This method handels the get request from the User.
            The method adds a new iteration to the experiment.

        Returns:
            HttpResponseRedirect: Redirects to the home view
            --or--
            HttpResponseRedirect: Redirects to the details view of the new iteration
        """
        experiment = ExperimentModel.objects.get(id=kwargs.get("detail_id"))
        version = VersionModel.objects.get(Q(experiment_id=experiment.id) & Q(edits=kwargs.get("edits")) & Q(runs=kwargs.get("runs")))
        if experiment.creator == request.user:
            if version.error is None:
                maxVersion = VersionModel.objects.all().filter(experiment_id=experiment.id).filter(edits=kwargs.get("edits")).aggregate(Max('runs'))
                newVersion = VersionModel()
                newVersion.minDimension = version.minDimension
                newVersion.maxDimension = version.maxDimension
                newVersion.numberSubspaces = version.numberSubspaces
                newVersion.parameterSettings = version.parameterSettings
                newVersion.experiment = experiment
                newVersion.edits = version.edits
                newVersion.status = "paused"
                newVersion.progress = 0
                newVersion.runs = maxVersion.get("runs__max") + 1
                maxSeed = VersionModel.objects.all().filter(experiment_id=experiment.id).filter(edits=kwargs.get("edits")).aggregate(Max('seed'))
                newVersion.seed = maxSeed.get("seed__max") + 1
                newVersion.save()
                for algo in version.algorithms.all():
                    newVersion.algorithms.add(algo)
                newVersion.save()
                experiment.latestVersion = str(newVersion.edits) + "." + str(newVersion.runs)
                experiment.latestStatus = "paused"
                experiment.save()
                return redirect("/details/" + str(experiment.id) + "/" + str(newVersion.edits) + "." + str(newVersion.runs))
        return redirect("/")

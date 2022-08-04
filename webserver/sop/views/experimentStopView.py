from django.shortcuts import redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from sop.models import ExperimentModel, VersionModel
from django.db.models import Q


class ExperimentStopView(View, LoginRequiredMixin):
    """ This class is a subclass of LoginRequiredMixin and View
    """

    def get(self, request, *args, **kwargs):
        """ This method handels the get request from the User.
            The method stops the running experiment.

        Returns:
            HttpResponseRedirect: Redirects to the detail view of the experiment
        """
        experiment = ExperimentModel.objects.get(id=kwargs.get("detail_id"))
        version = VersionModel.objects.get(Q(experiment_id=experiment.id) & Q(edits=kwargs.get("edits")) & Q(runs=kwargs.get("runs")))
        if experiment.creator == request.user:
            version.remove_container()

            version.status = "paused"
            version.experiment.latestVersion = str(version.edits) + "." + str(version.runs)
            version.experiment.latestStatus = "paused"
            version.experiment.save()
            version.save()

        return redirect("/details/" + str(experiment.id) + "/" + str(version.edits) + "." + str(version.runs))

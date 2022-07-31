from django.shortcuts import redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from sop.models import ExperimentModel, VersionModel
from django.db.models import Q


class ExperimentStartView(View, LoginRequiredMixin):
    """ This class is a subclass of LoginRequiredMixin and View
    """

    def get(self, request, *args, **kwargs):
        """ This method handels the get request from the User.
            The method start the experiment.

        Returns:
            HttpResponseRedirect: Redirects to the detail view of the experiment
        """
        experiment = ExperimentModel.objects.get(id=kwargs.get("detail_id"))
        version = VersionModel.objects.get(Q(experiment_id=experiment.id) & Q(edits=kwargs.get("edits")) & Q(runs=kwargs.get("runs")))
        if experiment.creator == request.user:
            if version.error is None:
                version.status = "running"
                version.experiment.latestVersion = str(version.edits) + "." + str(version.runs)
                version.experiment.latestStatus = "running"
                version.experiment.save()
                version.save()
                # todo: start it here
        return redirect("/details/"+str(experiment.id)+"/"+str(version.edits)+"."+str(version.runs))

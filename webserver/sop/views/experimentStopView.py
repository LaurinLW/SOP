from django.shortcuts import redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from sop.models import ExperimentModel, VersionModel
from django.db.models import Q


class ExperimentStopView(View, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        experiment = ExperimentModel.objects.get(id=kwargs.get("detail_id"))
        version = VersionModel.objects.get(Q(experiment_id=experiment.id) & Q(edits=kwargs.get("edits")) & Q(runs=kwargs.get("runs")))
        if experiment.creator == request.user:
            version.status = "paused"
            version.experiment.latestVersion = str(version.edits) + "." + str(version.runs)
            version.experiment.latestStatus = "paused"
            version.experiment.save()
            version.save()
            # todo: kill process
            return redirect("/details/"+str(experiment.id)+"/"+str(version.edits)+"."+str(version.runs))

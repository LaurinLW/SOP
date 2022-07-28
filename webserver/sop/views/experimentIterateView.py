from sop.models import ExperimentModel, VersionModel
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import redirect
from django.db.models import Q, Max


class ExperimentIterateView(View, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        experiment = ExperimentModel.objects.get(id=kwargs.get("detail_id"))
        version = VersionModel.objects.get(Q(experiment_id=experiment.id) & Q(edits=kwargs.get("edits")) & Q(runs=kwargs.get("runs")))
        if experiment.creator == request.user:
            maxVersion = VersionModel.objects.all().filter(experiment_id=experiment.id).filter(edits=kwargs.get("edits")).aggregate(Max('runs'))
            newVersion = version
            newVersion.pk = None
            newVersion.experiment = experiment
            newVersion.status = "paused"
            newVersion.runs = maxVersion.get("runs__max") + 1
            maxSeed = VersionModel.objects.all().filter(experiment_id=experiment.id).filter(edits=kwargs.get("edits")).aggregate(Max('seed'))
            newVersion.seed = maxSeed.get("seed__max") + 1
            newVersion.save()
            experiment.latestVersion = str(newVersion.edits) + "." + str(newVersion.runs)
            experiment.latestStatus = "paused"
            experiment.save()
            return redirect("/details/"+str(experiment.id)+"/"+str(newVersion.edits)+"."+str(newVersion.runs))
        return redirect("/")
from django.views import View
from django.shortcuts import render, redirect
from sop.models.experimentModel import ExperimentModel
from sop.models.versionModel import VersionModel
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Max


class ExperimentDetailView(View, LoginRequiredMixin):
    """ This class is a subclass of LoginRequiredMixin and View
    """
    template_name = 'experimentDetails.html'

    def get(self, request, *args, **kwargs):
        """ This method handels the initial opening request of the experiment-detail-site

        Returns:
            HttpResponse: Return an HttpResponse whose content is filled with
            the result of calling django.shortcuts.render with the passed arguments
        """
        experiment = ExperimentModel.objects.get(id=kwargs.get("detail_id"))
        version = VersionModel.objects.get(Q(experiment_id=experiment.id) & Q(edits=kwargs.get("edits")) & Q(runs=kwargs.get("runs")))
        versions = VersionModel.objects.all().filter(experiment_id=experiment.id)
        if experiment.creator == request.user:
            return render(request, self.template_name, {"Experiment": experiment, "Version": version, "Versions": versions})
        return redirect("/")

    def post(self, request, *args, **kwargs):
        """ This method handels the post request of the experiment-detail-site

        Returns:
            HttpResponseRedirect: Redirects to one of the Versions
            -- or --
            HttpResponseRedirect: Redirects to the new Version
        """
        experiment = ExperimentModel.objects.get(id=kwargs.get("detail_id"))
        version = VersionModel.objects.get(Q(experiment_id=experiment.id) & Q(edits=kwargs.get("edits")) & Q(runs=kwargs.get("runs")))
        actionReq = request.POST.get("action", "")
        showReq = request.POST.get("show", 0)
        if actionReq == "delete":
            if experiment.creator == request.user:
                experiment.delete()
        elif actionReq == "start":
            if experiment.creator == request.user:
                version.status = "running"
                version.experiment.latestVersion = str(version.edits) + "." + str(version.runs)
                version.experiment.latestStatus = "running"
                version.experiment.save()
                version.save()
                # todo: start it here
                return redirect("/details/"+str(experiment.id)+"/"+str(version.edits)+"."+str(version.runs))
        elif actionReq == "abort":
            if experiment.creator == request.user:
                version.status = "paused"
                version.experiment.latestVersion = str(version.edits) + "." + str(version.runs)
                version.experiment.latestStatus = "paused"
                version.experiment.save()
                version.save()
                # todo: kill process
                return redirect("/details/"+str(experiment.id)+"/"+str(version.edits)+"."+str(version.runs))
        elif actionReq == "iterate":
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
        elif showReq != 0:
            return redirect("/details/"+str(experiment.id)+"/"+showReq)
        return redirect("/")

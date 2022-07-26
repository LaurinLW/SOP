import json
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect
from sop.handler.parameterHandler import ParameterHandler
from sop.models.experimentModel import ExperimentModel
from sop.models.versionModel import VersionModel
from sop.models.algorithmModel import AlgorithmModel
from sop.models.datasetModel import DatasetModel
from sop.handler.inputHandler import InputHandler


class ExperimentDuplicateView(LoginRequiredMixin, View):
    """ This class is a subclass of LoginRequiredMixin and View
    """
    template_name = 'duplicateExperiment.html'

    def get(self, request, *args, **kwargs):
        """ This method handels the initial opening request of the experiment-duplicate-site

        Returns:
            HttpResponse: Return an HttpResponse whose content is filled with
            the result of calling django.shortcuts.render with the passed arguments
        """
        experiment = ExperimentModel.objects.get(id=kwargs.get("detail_id"))
        version = VersionModel.objects.get(Q(experiment_id=experiment.id) & Q(edits=kwargs.get("edits")) & Q(runs=kwargs.get("runs")))
        possible_algorithms = AlgorithmModel.objects.all().filter(creator_id=request.user.id)  # own algorithms
        pyod_algorithms = AlgorithmModel.objects.all().filter(creator_id=None)  # pyod algorithms
        possible_datasets = DatasetModel.objects.all().filter(creator_id=request.user.id)  # own datasets
        if version.parameterSettings != "":
            selected_data = json.loads(version.parameterSettings)
        else:
            selected_data = None
        data = "["
        for algo in possible_algorithms:
            data += algo.parameters + ","
        data = data[:-1]
        data += "]"
        data = json.loads(data)
        return render(request, self.template_name, {"Algorithms": (possible_algorithms | pyod_algorithms), "name": experiment.name,
                      "Datasets": possible_datasets, "version": version, "selected_data": selected_data, "data": data})

    def post(self, request, *args, **kwargs):
        """ This method handels the post request of the experiment-detail-site

        Returns:
            HttpResponseRedirect: Redirects to the duplication
        """
        experiment = ExperimentModel.objects.get(id=kwargs.get("detail_id"))
        version = VersionModel.objects.get(Q(experiment_id=experiment.id) & Q(edits=kwargs.get("edits")) & Q(runs=kwargs.get("runs")))
        if InputHandler().checkInput(request):
            newExperiment = experiment
            newExperiment.pk = None
            newExperiment.dataset = DatasetModel.objects.get(pk=request.POST.get("dataset", experiment.dataset))
            newExperiment.name = request.POST.get("name", experiment.name)
            newExperiment.latestVersion = "1.0"
            newExperiment.latestStatus = "paused"
            newExperiment.save()
            newVersion = version
            newVersion.pk = None
            newVersion.edits = 1
            newVersion.runs = 0
            newVersion.status = "paused"
            newVersion.experiment = newExperiment
            newVersion.seed = request.POST.get("seed", newVersion.seed)
            newVersion.minDimension = request.POST.get("minDimension", newVersion.minDimension)
            newVersion.maxDimension = request.POST.get("maxDimension", newVersion.maxDimension)
            newVersion.numberSubspaces = request.POST.get("numberSubspaces", newVersion.numberSubspaces)
            newVersion.numberSubspaces = request.POST.get("numberSubspaces", newVersion.numberSubspaces)
            newVersion.save()
            newVersion.parameterSettings = ParameterHandler().getFullJsonString(request, newVersion)
            newVersion.save()
            return redirect("/details/"+str(newExperiment.id)+"/"+newExperiment.latestVersion)
        return redirect("/duplicate/" + str(experiment.id) + "/" + kwargs.get("edits") + "." + kwargs.get("runs"))
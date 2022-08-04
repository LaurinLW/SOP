from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from sop.models.algorithmModel import AlgorithmModel
from sop.models.datasetModel import DatasetModel
from django.shortcuts import render, redirect
from sop.forms.experimentForm import ExperimentForm
from sop.forms.versionForm import VersionForm
import json
from sop.handler.parameterHandler import ParameterHandler
from sop.handler.inputHandler import InputHandler
from django.contrib import messages


class ExperimentCreateView(LoginRequiredMixin, View):
    """ This class is a subclass of LoginRequiredMixin and View
    """
    template_name = 'newExperiment.html'

    def get(self, request, *args, **kwargs):
        """ This method handels the initial opening request of the newExperiment-site

        Returns:
            HttpResponse: Return an HttpResponse whose content is filled with
            the result of calling django.shortcuts.render with the passed arguments
        """
        possible_algorithms = AlgorithmModel.objects.all().filter(creator_id=request.user.id)  # own algorithms
        pyod_algorithms = AlgorithmModel.objects.all().filter(creator_id=None).order_by("name").values()  # pyod algorithms
        possible_datasets = DatasetModel.objects.all().filter(creator_id=request.user.id).order_by("name").values()  # own datasets
        algorithms = possible_algorithms | pyod_algorithms
        if algorithms.count() > 0:
            data = "["
            for algo in algorithms:
                data += algo.parameters + ","
            data = data[:-1]
            data += "]"
            data = json.loads(data)
        else:
            data = None
        categories = ["Probabilistic", "Linear Model", "Proximity-Based", "Outlier Ensembles", "Neural Networks", "Other"]
        return render(request, self.template_name, {"Algorithms": algorithms, "Datasets": possible_datasets, "data": data, "categories": categories})

    def post(self, request, *args, **kwargs):
        """ This method handels the post request of the newExperiment-site

        Returns:
            HttpResponseRedirect: Redirects to the detail View of the created Experiment
        """
        if InputHandler().checkInput(request):
            experiment_form = ExperimentForm(request.POST)
            version_form = VersionForm(request.POST)
            if experiment_form.is_valid() and version_form.is_valid():
                experiment_form.creator = request.user
                experiment_form.dataset = DatasetModel.objects.get(pk=request.POST["dataset"])
                exp = experiment_form.save()
                version_form.experiment = exp
                ver = version_form.save()
                parameters = ParameterHandler().getFullJsonString(request, ver)
                if type(parameters) != str:
                    exp.delete()
                    ver.delete()
                    return redirect("/newExperiment")
                ver.parameterSettings = parameters
                ver.save()
                reps = int(request.POST.get("repetitions", 1)) - 1
                for a in range(reps):
                    ver.pk = None
                    ver.runs += 1
                    ver.seed += 1
                    ver.save()
                    exp.latestVersion = str(ver.edits) + "." + str(ver.runs)
                    exp.save()
                return redirect("/details/" + str(exp.id) + "/" + exp.latestVersion)
            else:
                messages.warning(request, "There was a problem with your input form")
        return redirect("/newExperiment")

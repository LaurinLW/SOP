from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from sop.models import ExperimentModel, VersionModel, ResultModel
from django.http import HttpResponse
import os


class ExperimentResultView(View, LoginRequiredMixin):
    """ This class is a subclass of LoginRequiredMixin and View
    """
    template_name = 'experimentResults.html'

    def get(self, request, *args, **kwargs):
        """ This method handels the get request from the User.
            The method trys to show the results of the experiment to the User.
            The User can also download each result

        Returns:
            HttpResponseRedirect: Redirects to the home view
            --or--
            HttpResponse: Return an HttpResponse whose content is filled with
            the result of calling django.shortcuts.render with the passed arguments
        """
        experiment = ExperimentModel.objects.get(id=kwargs.get("detail_id"))
        version = VersionModel.objects.get(Q(experiment_id=experiment.id) & Q(edits=kwargs.get("edits")) & Q(runs=kwargs.get("runs")))
        results = ResultModel.objects.all().filter(version_id=version.id)
        if kwargs.get("result_id", 0) == 0:
            if experiment.creator == request.user:
                return render(request, self.template_name, {"version": version, "results": results})
            return "/"
        else:
            if experiment.creator == request.user:
                file_id = kwargs.get("result_id")
                result = ResultModel.objects.get(pk=file_id)
                response = HttpResponse(result.resultFile.read(), 'text/plain')
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(result.resultFile.path)
                return response
            return "/"

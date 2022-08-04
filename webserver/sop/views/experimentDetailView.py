from django.views import View
from django.shortcuts import render, redirect
from sop.models.experimentModel import ExperimentModel
from sop.models.versionModel import VersionModel
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse


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
        if experiment.creator == request.user and request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return render(request, self.template_name, {"Experiment": experiment, "Version": version, "Versions": versions})
        elif request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            update_progress = f'{version.progress}'
            update_status = f'{version.status}'
            return JsonResponse({"update_progress": update_progress, "update_status": update_status})
        return redirect("/")

    def post(self, request, *args, **kwargs):
        """ This method handels the post request of the experiment-detail-site

        Returns:
            HttpResponseRedirect: Redirects to one of the Versions
            -- or --
            HttpResponseRedirect: Redirects to the home view
        """
        experiment = ExperimentModel.objects.get(id=kwargs.get("detail_id"))
        showReq = request.POST.get("show", 0)
        if showReq != 0:
            return redirect("/details/" + str(experiment.id) + "/" + showReq)
        return redirect("/")

from django.shortcuts import redirect
from django.views import View
from sop.models import ExperimentModel
from django.contrib.auth.mixins import LoginRequiredMixin


class ExperimentDeleteView(View, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        experiment = ExperimentModel.objects.get(id=kwargs.get("detail_id"))
        if experiment.creator == request.user:
            experiment.delete()
        return redirect("/")

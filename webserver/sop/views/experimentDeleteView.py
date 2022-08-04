from django.shortcuts import redirect
from django.views import View
from sop.models import ExperimentModel
from django.contrib.auth.mixins import LoginRequiredMixin


class ExperimentDeleteView(View, LoginRequiredMixin):
    """ This class is a subclass of LoginRequiredMixin and View
    """
    def get(self, request, *args, **kwargs):
        """ This method handels all delete-experiment requests from Users

        Returns:
            HttpResponseRedirect: Return an HttpResponseRedirect to the Home-View
        """
        experiment = ExperimentModel.objects.get(id=kwargs.get("detail_id"))
        if experiment.creator == request.user:
            experiment.delete()
        return redirect("/")

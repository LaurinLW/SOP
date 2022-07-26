from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from sop.models.experimentModel import ExperimentModel
from django.views import View


class HomeView(LoginRequiredMixin, View):
    """ This class is a subclass of LoginRequiredMixin and View
    """
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        """ This method handels all home requests from Users

        Returns:
            HttpResponse: Return an HttpResponse whose content is filled with
            the result of calling django.shortcuts.render with the passed arguments
        """
        experiments_context = ExperimentModel.objects.all().filter(creator_id=request.user.id)
        return render(request, self.template_name, {'Experiments': experiments_context})

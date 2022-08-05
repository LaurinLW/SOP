from django.views import View
from sop.models import ExperimentModel, VersionModel
from django.db.models import Q
from django.shortcuts import render, redirect
import sop.metrics as metrics
import inspect


class ExperimentDashboardView(View):
    """Provides the dashboard for an experiment.
    """

    TEMPLATE_NAME = 'experimentDashboard.html'
    DEFAULT_METRIC = 'TestMetric'

    def __init__(self):
        """Constructs a new ExperimentDashboardView.
        Automatically loads all metrics classes in the 'metrics' package.
        """

        self._metrics = dict()
        for name, obj in inspect.getmembers(metrics, inspect.isclass):
            if name == "Metric":
                continue
            if len(inspect.getmro(obj)) >= 2 and inspect.getmro(obj)[1] == metrics.Metric:
                self._metrics[name] = obj

    def get(self, request, *args, **kwargs):
        """Handles the HTTP GET requests
        """
        experiment = ExperimentModel.objects.get(id=kwargs.get("detail_id"))
        version = VersionModel.objects.get(Q(experiment_id=experiment.id) & Q(edits=kwargs.get("edits")) & Q(runs=kwargs.get("runs")))

        if not experiment.creator == request.user:
            redirect("/")

        metric_name = kwargs.get("metric", "")
        if metric_name == "":
            redirect("/dashboard/"
                     + str(kwargs.get("detail_id"))
                     + "/" + str(kwargs.get("edits"))
                     + "." + str(kwargs.get("runs"))
                     + "/" + self.DEFAULT_METRIC)

        used_metric = None

        # disabled because metrics are currently not serializable
        # if "metric" in request.session.keys:
        #     saved_metric = request.session.get("metric")

        #     if saved_metric.__class__.__name__ == metric_name:
        #         # requested metric already stored in session. use that metric object
        #         used_metric = saved_metric
        #     else:
        #         # different metric stored. create new metric object that matches request
        #         if metric_name in self._metrics.keys():
        #             used_metric = self._metrics[metric_name](version)
        #         else:
        #             used_metric = self._metrics[self.DEFAULT_METRIC](version)

        # else:
        # no metric saved in session. create a new one
        if metric_name in self._metrics.keys():
            used_metric = self._metrics[metric_name](version)
        else:
            used_metric = self._metrics[self.DEFAULT_METRIC](version)

        # disabled because metrics are currently not serializable
        # request.session["metric"] = used_metric

        # apply filter to metric
        filter = request.GET.get('filter', '')
        used_metric.filter(filter)

        page = int(request.GET.get("page", 0))
        if (page - 1 > used_metric.view.get_pages()):
            page = 0  # should this instead be an error?

        prevPage = max(-1, page - 1)
        nextPage = -1
        if page < used_metric.view.get_pages() - 1:
            nextPage = page + 1

        return render(request,
                      self.TEMPLATE_NAME,
                      {"metricView": used_metric.view.view(page),
                       "metrics": self._metrics.keys(),
                       "version": version,
                       "selectedMetric": used_metric.__class__.__name__,
                       "currentPage": page,
                       "nextPage": nextPage,
                       "prevPage": prevPage})

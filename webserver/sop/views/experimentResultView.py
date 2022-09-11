from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from sop.models import ExperimentModel, VersionModel, ResultModel
from django.http import HttpResponse
import os
from zipfile import ZipFile
import io


class ExperimentResultView(View, LoginRequiredMixin):
    """ This class is a subclass of LoginRequiredMixin and View
    """
    template_name = 'experimentResults.html'

    def get(self, request, *args, **kwargs):
        """ This method handels all result requests from Users

        Returns:
            HttpResponse: Return an HttpResponse whose content is filled with
            the result of calling django.shortcuts.render with the passed arguments
        """
        try:
            experiment = ExperimentModel.objects.get(id=kwargs.get("detail_id"))
            version = VersionModel.objects.get(Q(experiment_id=experiment.id) & Q(edits=kwargs.get("edits")) & Q(runs=kwargs.get("runs")))
        except:
            return redirect("/home")
        results = ResultModel.objects.all().filter(version_id=version.id)
        if kwargs.get("result_id", 0) == 0:
            if (experiment.creator == request.user):
                return render(request, self.template_name, {"version": version, "results": results})
            return ("/")
        else:
            if experiment.creator == request.user:
                file_id = kwargs.get("result_id")
                if file_id != "all" and str(file_id).isnumeric():
                    result = ResultModel.objects.get(pk=file_id)
                    response = HttpResponse(result.resultFile.read(), 'text/plain')
                    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(result.resultFile.path)
                    return response
                elif file_id == "all":
                    buffer = io.BytesIO()
                    zip_file = ZipFile(buffer, 'w')
                    for result in results:
                        zip_file.write(result.resultFile.path, os.path.basename(result.resultFile.path))
                    zip_file.close()
                    response = HttpResponse(buffer.getvalue())
                    response['Content-Type'] = 'application/x-zip-compressed'
                    response['Content-Disposition'] = f'inline; filename={experiment.name}.{version.edits}.{version.runs}.zip'
                    return response
            return ("/")

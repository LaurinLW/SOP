from django.views import View
from ..forms.algorithmForm import AlgorithmForm
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models.algorithmModel import AlgorithmModel
from django.shortcuts import render, redirect
from django.contrib import messages
import importlib
import os
import inspect


class AlgorithmUploadView(View, LoginRequiredMixin):

    template_name = 'uploadAlgorithm.html'

    def get(self, request, *args, **kwargs):
        """ This method processes the initial opening request of the algorithm upload.

        Returns:
            HttpResponse: Return an HttpResponse whose content is filled with
            the result of calling django.shortcuts.render with the passed arguments
        """
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        """ This method processes the post request of the algorithm upload

        Returns:
            HttpResponseRedirect: Redirects to the user profile
        """
        if "upload_btn" in request.POST:
            algorithm_form = AlgorithmForm(request.POST, request.FILES)
            file = request.FILES.get('file')
            # checking if the uploaded file is non existent
            if file is None:
                messages.warning(request, "Upload file can not be empty!")
                return redirect('/uploadAlgorithm')
            algorithm_name = request.POST.get('name')
            # checking if there is a name assigned to the algorithm
            if algorithm_name is None or not algorithm_name:
                messages.warning(request, "'name' cant be empty!")
                return redirect('/uploadAlgorithm')
            # checking if the name has already been assigned to another algorithm
            if AlgorithmModel.objects.all().filter(name=algorithm_name).filter(creator=request.user).exists():
                messages.warning(request, "This name has already been assigned to another algorithm!")
                return redirect('/uploadAlgorithm')
            if algorithm_form.is_valid():
                # saving parameters that have been provided by the user
                algorithm_form.creator = request.user
                algo = algorithm_form.save()
                algo.category = request.POST.get('category')
                # reading out the provided python file to extract names and parameters
                try:
                    spec = importlib.util.spec_from_file_location(algo.name, algo.file.path)
                    module = importlib.util.module_from_spec(spec)
                    module.__package__ = "sop.views.user_algorithms"
                    spec.loader.exec_module(module)
                    basename = os.path.basename(algo.file.path)
                    module_name = module.__package__ + "." + basename.replace(".py", "")
                    for class_name, cls in inspect.getmembers(importlib.import_module(module_name), inspect.isclass):
                        if module.__package__ == cls.__module__.replace("." + basename[:-3], ""):
                            algorithm = getattr(module, class_name)
                            parameters = inspect.getargspec(algorithm)
                            algoPara = "{" + f"\"ID\": {algo.id},\n"
                            for i in range(1, len(parameters.args)):
                                default_type = type(parameters.defaults[i - 1])
                                if default_type == int or default_type == float:
                                    algoPara += (f"\"{parameters.args[i]}\": {parameters.defaults[i-1]},\n")
                                elif default_type == bool:
                                    if bool:
                                        algoPara += (f"\"{parameters.args[i]}\": true,\n")
                                    else:
                                        algoPara += (f"\"{parameters.args[i]}\": false,\n")
                                elif default_type == list:
                                    algoPara += (f"\"{parameters.args[i]}\": {parameters.defaults[i-1]},\n")
                                elif parameters.defaults[i - 1] is None:
                                    algoPara += (f"\"{parameters.args[i]}\": null,\n")
                                else:
                                    default = str(parameters.defaults[i - 1]).split(" at ")[0]
                                    if default != str(parameters.defaults[i - 1]):
                                        algoPara += (f"\"{parameters.args[i]}\": \"{default}>\",\n")
                                    else:
                                        algoPara += (f"\"{parameters.args[i]}\": \"{parameters.defaults[i-1]}\",\n")
                            algoPara = algoPara[:-2]
                            algoPara += "}"
                            algo.parameters = algoPara
                            algo.modul_name = algo.name
                            algo.class_name = class_name
                except:
                    messages.warning(request, "An error has occured when trying to extract parameters out of the provided python algorithm code!")
                    algo.delete()
                    return redirect('/uploadAlgorithm')
                if (algo.parameters is None or algo.modul_name is None or algo.class_name is None):
                    algo.delete()
                    messages.warning(request, "An error has occured when trying to extract parameters out of the provided python algorithm code!")
                    return redirect('/uploadAlgorithm')
                algo.save()
        return redirect("/profile")

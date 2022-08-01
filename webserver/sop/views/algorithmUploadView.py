from django.views import View
from ..forms.algorithmForm import AlgorithmForm
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models.algorithmModel import AlgorithmModel
from django.shortcuts import render, redirect
from django.contrib import messages


class AlgorithmUploadView(View, LoginRequiredMixin):

    template_name = 'uploadAlgorithm.html'

    def get(self, request, *args, **kwargs):
        algorithms = AlgorithmModel.objects.all().filter(creator_id=request.user.id)  # own algorithms
        return render(request, self.template_name, {
            "algorithms": algorithms
        })

    def post(self, request, *args, **kwargs):
        if "upload_btn" in request.POST:
            algorithm_form = AlgorithmForm(request.POST, request.FILES)
            file = request.FILES.get('file')
            # checking if the uploaded file is non existent
            if file is None:
                messages.warning(request, "Upload file can not be empty!")
                return redirect('/uploadAlgorithm')
            algorithm_name = request.POST.get('name')
            # checking if there is a name assigned to the algorithm
            if algorithm_name is None:
                messages.warning(request, "'name' cant be empty!")
                return redirect('/uploadAlgorithm')
            # checking if the assigned name is not being used for another algorithm
            # if AlgorithmModel.objects.all().filter(name=algorithm_name) != None:
            #    messages.warning(request, "This name has already been assigned to another user algorithm!")
            #    return redirect('/uploadAlgorithm')

            if algorithm_form.is_valid():
                algorithm_form.creator = request.user
                algo = algorithm_form.save()
                algo.category = request.POST.get('category')
                idalgo = "\"ID\": " + str(algo.id) + ",\n"
                algo.parameters = "{\n" + idalgo + str(self.returnDict(self.readLines(algo))) + "\n}"
                algo.save()
        else:
            print("nichts passiert...")
        return redirect("/profile")

    def returnDict(self, params):
        nameList = ""
        defaultList = ""
        string = ""
        for param in params:
            split = param.split("=")
            nameList = split[0]
            defaultList = split[1]
            string += '"' + nameList + '"' + ": " + '"' + defaultList + '"' + ",\n"
        return string[:-2]

    def readLines(self, algo):
        with algo.file.open('r') as f:
            lines = f.readlines()
            for line in lines:
                if "def __init__(" in line:
                    return self.removePreSuffix(line)
        return None

    def removePreSuffix(self, string: str):
        return self.createArgList(string.replace(" ", "").removeprefix("def__init__(self,").strip().removesuffix("):"))

    def createArgList(self, string: str):
        return string.split(",")

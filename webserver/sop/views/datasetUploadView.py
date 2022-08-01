from django.views import View
from ..forms.datasetForm import DatasetForm
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models.datasetModel import DatasetModel
from django.shortcuts import render, redirect
from django.contrib import messages


class DatasetUploadView(View, LoginRequiredMixin):

    template_name = 'uploadDataset.html'

    def get(self, request, *args, **kwargs):
        datasets = DatasetModel.objects.all().filter(creator_id=request.user.id)  # own algorithms
        return render(request, self.template_name, {
            "datasets": datasets
        })

    def post(self, request, *args, **kwargs):
        if "upload_btn" in request.POST:
            # checking if the uploaded file is non existent
            if request.FILES.get('file') is None:
                messages.warning(request, "Uploaded dataset can not be empty!")
                return redirect('uploadDataset')
            dataset_name = request.POST.get('name')
            # checking if there is a name assigned to the dataset
            if dataset_name is None:
                messages.warning(request, "'name' can not be empty!")
                return redirect('/uploadDataset')
            # checking if the assigned name is not being used for another dataset
            # if DatasetModel.objects.all().filter(name=dataset_name) != None:
            #     messages.warning(request, "This name has already been assigned to another dataset!")
            #     return redirect('/uploadDataset')
            dataset_form = DatasetForm(request.POST, request.FILES)
            if (dataset_form.is_valid()):
                dataset_form.creator = request.user
                dataset = dataset_form.save()
                dataset.save()
                print(dataset.name)
        else:
            print("nichts passiert...")
        return redirect("/profile")

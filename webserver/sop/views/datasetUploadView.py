from django.views import View
from ..forms.datasetForm import DatasetForm
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models.datasetModel import DatasetModel
from django.shortcuts import render, redirect


class DatasetUploadView(View, LoginRequiredMixin):

    template_name = 'uploadDataset.html'

    def get(self, request, *args, **kwargs):
        datasets = DatasetModel.objects.all().filter(creator_id=request.user.id)  # own algorithms
        return render(request, self.template_name, {
            "datasets": datasets
            })

    def post(self, request, *args, **kwargs):
        if "upload_btn" in request.POST:
            dataset_form = DatasetForm(request.POST, request.FILES)
            if (dataset_form.is_valid()):
                dataset_form.creator = request.user
                dataset = dataset_form.save()
                dataset.save()
                print(dataset.name)
        else:
            print("nichts passiert...")
        return redirect("/home")

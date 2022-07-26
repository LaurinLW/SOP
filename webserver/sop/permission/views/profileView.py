from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View


import os

from django.contrib.auth.models import User
from sop.models.algorithmModel import AlgorithmModel
from sop.models.datasetModel import DatasetModel


class ProfileView(View, LoginRequiredMixin):
    """ This class is a subclass of View and LoginRequiredMixin
    """
    user_template = 'userProfile.html'
    admin_template = 'adminProfile.html'

    def get(self, request, *args, **kwargs):
        username = request.user  # name of logged in user
        email = request.user.email  # email of logged in user
        user_algorithms = AlgorithmModel.objects.all().filter(creator_id=request.user.id)  # user algorithms
        datasets = DatasetModel.objects.all().filter(creator_id=request.user.id)
        if request.user.is_superuser:
            user_list = User.objects.all()
            print(user_list)
            return render(request, self.admin_template, {
                "user_list": user_list,
                "username": username,
                "email": email,
                "algorithm": user_algorithms,
                "datasets": datasets
                })
        else:
            return render(request, self.user_template, {"username": username, "email": email, "algorithm": user_algorithms, "datasets": datasets})

    def post(self, request, *args, **kwargs):
        if request.user.is_superuser:
            print("ADMIN...")
        else:
            print("kein admin,...")
        if 'delete_algorithm' in request.POST:
            algo = AlgorithmModel.objects.get(pk=request.POST.get('delete_algorithm'))
            if os.path.isfile(algo.file.path):
                os.remove(algo.file.path)
            algo.delete()
        elif 'delete_dataset' in request.POST:
            dataset = DatasetModel.objects.get(pk=request.POST.get('delete_dataset'))
            if os.path.isfile(dataset.file.path):
                os.remove(dataset.file.path)
            dataset.delete()
        elif 'delete_user' in request.POST and request.user.is_superuser:
            user = User.objects.get(pk=request.POST.get('delete_user'))
            user.delete()
        elif 'promote_user' in request.POST:
            user = User.objects.get(pk=request.POST.get('promote_user'))
            user.is_staff = True
            user.is_superuser = True
            user.save()
        elif 'degrade_user' in request.POST and request.user.is_superuser:
            user = User.objects.get(pk=request.POST.get('degrade_user'))
            user.is_staff = False
            user.is_superuser = False
            user.save()
        return redirect("/profil")

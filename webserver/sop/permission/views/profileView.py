from django.shortcuts import render, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
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
        datasets = DatasetModel.objects.all().filter(creator_id=request.user.id)  # user datasets

        # Pagination algorithms
        algo_page = request.GET.get('algo_page', 1)
        algoritihm_paginator = Paginator(user_algorithms, 3)

        try:
            algos = algoritihm_paginator.page(algo_page)
        except PageNotAnInteger:
            algos = algoritihm_paginator.page(1)
        except EmptyPage:
            algos = algoritihm_paginator.page(algoritihm_paginator.num_pages)

        # Pagination datasets
        dataset_page = request.GET.get('dataset_page', 1)
        dataset_paginator = Paginator(datasets, 2)

        try:
            datas = dataset_paginator.page(dataset_page)
        except PageNotAnInteger:
            datas = dataset_paginator.page(1)
        except EmptyPage:
            datas = dataset_paginator.page(dataset_paginator.num_pages)

        if request.user.is_superuser and request.user.is_staff:
            users = User.objects.all()

            # Pagination users
            user_page = request.GET.get('user_page', 1)
            user_paginator = Paginator(users, 2)

            try:
                users = user_paginator.page(user_page)
            except PageNotAnInteger:
                users = user_paginator.page(1)
            except EmptyPage:
                users = user_paginator.page(user_paginator.num_pages)

            return render(request, self.admin_template, {
                "username": username,
                "email": email,
                "algos": algos,
                "datas": datas,
                "users": users
            })
        else:
            return render(request, self.user_template, {
                "username": username,
                "email": email,
                "algos": algos,
                "datas": datas
            })

    def post(self, request, *args, **kwargs):
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
        elif 'promote_user' in request.POST and request.user.is_superuser:
            user = User.objects.get(pk=request.POST.get('promote_user'))
            user.is_staff = True
            user.is_superuser = True
            user.save()
        elif 'degrade_user' in request.POST and request.user.is_superuser:
            user = User.objects.get(pk=request.POST.get('degrade_user'))
            user.is_staff = False
            user.is_superuser = False
            user.save()
        return redirect("/profile")

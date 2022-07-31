from django.urls import path
from sop.permission.views import loginView, registerView, logoutView, profileView
from sop.views import homeView, experimentCreateView, experimentDetailView, experimentDuplicateView, experimentEditView, experimentStartView
from sop.views import algorithmUploadView, datasetUploadView, experimentStopView, experimentDeleteView, experimentIterateView, experimentResultView
from modernrpc.views import RPCEntryPoint

urlpatterns = [
    path('profil', profileView.ProfileView.as_view()),
    path('login', loginView.LoginView.as_view()),
    path('register', registerView.RegisterView.as_view()),
    path('logout', logoutView.LogoutView.as_view()),
    path('', homeView.HomeView.as_view()),
    path('home', homeView.HomeView.as_view()),
    path('newExperiment', experimentCreateView.ExperimentCreateView.as_view()),
    path('details/<int:detail_id>/<str:edits>.<str:runs>', experimentDetailView.ExperimentDetailView.as_view()),
    path('details/<int:detail_id>/delete', experimentDeleteView.ExperimentDeleteView.as_view()),
    path('details/<int:detail_id>/<str:edits>.<str:runs>/start', experimentStartView.ExperimentStartView.as_view()),
    path('details/<int:detail_id>/<str:edits>.<str:runs>/results', experimentResultView.ExperimentResultView.as_view()),
    path('details/<int:detail_id>/<str:edits>.<str:runs>/results/<str:result_id>', experimentResultView.ExperimentResultView.as_view()),
    path('details/<int:detail_id>/<str:edits>.<str:runs>/iterate', experimentIterateView.ExperimentIterateView.as_view()),
    path('details/<int:detail_id>/<str:edits>.<str:runs>/stop', experimentStopView.ExperimentStopView.as_view()),
    path('edit/<int:detail_id>/<str:edits>.<str:runs>', experimentEditView.ExperimentEditView.as_view()),
    path('duplicate/<int:detail_id>/<str:edits>.<str:runs>', experimentDuplicateView.ExperimentDuplicateView.as_view()),
    path('uploadAlgorithm', algorithmUploadView.AlgorithmUploadView.as_view()),
    path('uploadDataset', datasetUploadView.DatasetUploadView.as_view()),
    path('rpc', RPCEntryPoint.as_view())
]

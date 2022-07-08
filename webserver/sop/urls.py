from django.urls import path
from .permission.views import loginView, registerView, logoutView


urlpatterns = [
    path('', loginView.login_request, name='login'),
    path('register', registerView.register_request, name="register"),
    path('logout', logoutView.logout_request, name="logout"),
]

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages


def login_request(request):
    """ This method handels the login requests from Users

    Args:
        request (HttpRequest):

    Returns:
        HttpResponse: Return an HttpResponse whose content is filled with
        the result of calling django.shortcuts.render with the passed arguments
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    form = AuthenticationForm
    return render(request, "login.html", {"login_form": form})

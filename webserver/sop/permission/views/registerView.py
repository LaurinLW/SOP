from django.shortcuts import render, redirect
from ...forms.newUserForm import NewUserForm
from django.contrib.auth import login
from django.contrib import messages


def register_request(request):
    """ This method handels the register requests from Users

    Args:
        request (HttpRequest):

    Returns:
        HtppResponse: Return an HttpResponse whose content is filled with
        the result of calling django.shortcuts.render with the passed arguments
    """
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
        messages.error(request, "Invalid information")
    form = NewUserForm()
    return render(request, "register.html", {"register_form": form})

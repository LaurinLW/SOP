from django.shortcuts import redirect
from django.contrib.auth import logout


def logout_request(request):
    """ This method handels the logout requests from Users

    Args:
        request (HttpRequest):


    Returns:
        HttpResponseRedirect: Redirects to the url in the argument
    """
    logout(request)
    return redirect("login")

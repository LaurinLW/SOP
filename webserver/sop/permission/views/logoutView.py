from django.shortcuts import redirect
from django.contrib.auth import logout
from django.views import View


class LogoutView(View):
    """ This class is a subclass of View
    """

    def get(self, request, *args, **kwargs):
        """ This method handels the logout requests from Users

        Returns:
            HttpResponseRedirect: Redirects to the url in the argument
        """
        logout(request)
        return redirect("/login")

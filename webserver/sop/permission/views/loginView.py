from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views import View


class LoginView(View):
    """ This class is a subclass of View
    """
    form_class = AuthenticationForm
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        """ This method handels the initial opening request of the login-site

        Returns:
            HttpResponse: Return an HttpResponse whose content is filled with
            the result of calling django.shortcuts.render with the passed arguments
        """
        form = self.form_class()
        return render(request, self.template_name, {"login_form": form})

    def post(self, request, *args, **kwargs):
        """ This method handels the post request of the login-site

        Returns:
            HttpResponse: Return an HttpResponse whose content is filled with
            the result of calling django.shortcuts.render with the passed arguments
            -- or --
            HttpResponseRedirect: Redirects to the url in the argument
        """
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/home")
        messages.warning(request, "Invalid username or password")
        return redirect("/login")

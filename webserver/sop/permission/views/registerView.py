from django.shortcuts import render, redirect
from sop.forms.newUserForm import NewUserForm
from django.contrib.auth import login
from django.contrib import messages
from django.views import View
from django.contrib.auth.models import User
import json


class RegisterView(View):
    """ This class is a subclass of View
    """
    form_class = NewUserForm
    template_name = 'register.html'

    def get(self, request, *args, **kwargs):
        """ This method handels the initial opening request of the register-site

        Returns:
            HtppResponse: Return an HttpResponse whose content is filled with
            the result of calling django.shortcuts.render with the passed arguments
        """
        form = self.form_class()
        return render(request, self.template_name, {'register_form': form})

    def post(self, request, *args, **kwargs):
        """ This method handels the post request of the register-site

        Returns:
            HttpResponse: Return an HttpResponse whose content is filled with
            the result of calling django.shortcuts.render with the passed arguments
            -- or --
            HttpResponseRedirect: Redirects to the url in the argument
        """
        form = NewUserForm(request.POST)
        if form.is_valid():
            if User.objects.all().filter(username=request.POST.get("username")).count() > 0:
                messages.error(request, "This username is already taken")
                return redirect("/register")
            user = form.save()
            login(request, user)
            return redirect("/home")
        error_json = json.loads(form.errors.as_json())
        for error in error_json:
            messages.error(request, error_json[error][0]["message"])
        form = self.form_class()
        return render(request, self.template_name, {'register_form': form})

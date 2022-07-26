from django.shortcuts import render, redirect
from ...forms.newUserForm import NewUserForm
from django.contrib.auth import login
from django.contrib import messages
from django.views import View


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
            user = form.save()
            login(request, user)
            return redirect("/home")
        messages.error(request, "Invalid information")
        form = self.form_class()
        return render(request, self.template_name, {'register_form': form})

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class NewUserForm(UserCreationForm):
    """ This class is the subclass of the UserCreationForm.
        This form has the purpose to create a new User
    """
    email = forms.EmailField(required=True)

    class Meta:
        """ The Meta class contains the Meta-information about the Form
        """
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        """ The save method saves the object to the database.

        Args:
            commit (bool, optional): Defaults to True.

        Returns:
            User: returns the saved user
        """
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

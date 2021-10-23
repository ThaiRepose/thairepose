from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class CreateUserForm(UserCreationForm):
    """Config user form class."""

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        """Check email is avaliable or not.

        Raises:
            forms.ValidationError: raise message if email is already exist

        Returns:
            str: user email
        """
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use. \
                                        Please supply a different email address.")

        return email

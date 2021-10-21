"""Contain form class."""
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CreateUserForm(UserCreationForm):
    """Config user form class."""

    class Meta:
        """Subclass of user form."""

        model = User
        fields = ['username', 'email', 'password1', 'password2']

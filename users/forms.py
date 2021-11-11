from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserUpdateForm(forms.ModelForm):
    """Class for set field of user form."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ProfileUpdateForm(forms.ModelForm):
    """Class for set field of profile form."""

    class Meta:
        model = Profile
        fields = ['birthday', 'profile_pic']

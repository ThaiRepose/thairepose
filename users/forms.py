from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserUpdateForm(forms.ModelForm):
    """Class for set field of user form."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'size': '8',
                'class': 'appearance-none block w-full bg-white text-black border border-gray-200 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white focus:border-gray-500 w-full',
            }),
            'last_name': forms.TextInput(attrs={
                'size': '10',
                'class': 'appearance-none block w-full bg-white text-black border border-gray-200 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white focus:border-gray-500 w-full',
            }),
        }


class ProfileUpdateForm(forms.ModelForm):
    """Class for set field of profile form."""

    class Meta:
        model = Profile
        fields = ['birthday', 'profile_pic']

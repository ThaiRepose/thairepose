from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserUpdateForm(forms.ModelForm):
    """Class for set field of user form."""

    first_name = forms.CharField().required
    last_name = forms.CharField().required
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name' : forms.TextInput(attrs={ 'maxlength': 10,}),
        }

class ProfileUpdateForm(forms.ModelForm):
    """Class for set field of profile form."""

    class Meta:
        model = Profile
        fields = ['birthday', 'profile_pic']

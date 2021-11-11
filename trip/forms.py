from django import forms
from .models import TripPlan

choice_list = ['Uncategorize']


class TripPlanForm(forms.ModelForm):
    """Class for create trip form."""

    class Meta:
        model = TripPlan
        fields = ('title', 'duration', 'price', 'category', 'body')
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'min': '0'}),
            'price': forms.NumberInput(attrs={'min': '0'})
        }
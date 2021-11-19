from django import forms
from .models import TripPlan, UploadImage, Review

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


class TripPlanImageForm(forms.ModelForm):
    """Class for upload images form."""

    class Meta:
        model = UploadImage
        fields = ('image',)


class ReviewForm(forms.ModelForm):
    """Class for create review form."""

    class Meta:
        model = Review
        fields = ['body']

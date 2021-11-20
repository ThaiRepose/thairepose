from django import forms
from django.forms import widgets
from .models import TripPlan, UploadImage, Review
from mptt.forms import TreeNodeChoiceField

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

    parent = TreeNodeChoiceField(queryset=Review.objects.all())

    def __inti__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = Review
        fields = ('parent', 'body')
        widgets = {
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }
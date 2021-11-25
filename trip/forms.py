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
            'title': forms.TextInput(attrs={
                'class': 'appearance-none block w-full bg-white text-black border border-gray-200 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white focus:border-gray-500 w-full',
                'placeholder': 'Title'
            }),
            'category': forms.Select(attrs={
                'class': 'block appearance-none w-full bg-white border border-gray-200 text-black py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500',
            }),
            'duration': forms.NumberInput(attrs={
                'min': '0',
                'class': "appearance-none block w-full bg-white text-black border border-gray-200 rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white focus:border-gray-500",
                'placeholder': 'Duration'
            }),
            'price': forms.NumberInput(attrs={
                'min': '0',
                'class': "appearance-none block w-full bg-white text-black border border-gray-200 rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white focus:border-gray-500",
                'placeholder': 'price'
            })
        }


class TripPlanImageForm(forms.ModelForm):
    """Class for upload images form."""

    class Meta:
        model = UploadImage
        fields = ('image',)


class ReviewForm(forms.ModelForm):
    """Class for create review form."""

    parent = TreeNodeChoiceField(queryset=Review.objects.all(), required=False,
                                 widget=forms.Select(attrs={'class': 'invisible'}))

    def __inti__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)

        self.fields['parent'].widget.attrs.update({'class': 'invisible'})
        self.fields['parent'].label = ''
        self.fields['parent'].required = False

    class Meta:
        model = Review
        fields = ['parent', 'body']

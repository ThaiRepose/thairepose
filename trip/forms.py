from django import forms
from .models import TripPlan, CategoryPlan


# choice = CategoryPlan.objects.all().values_list('name', 'name')
choice_list = ['Uncategorize']
# for item in choice:
#     if item not in choice_list:
#         choice_list.append(item)


class TripPlanForm(forms.ModelForm):
    """Class for create trip form."""

    class Meta:
        model = TripPlan
        fields = ('title', 'author', 'duration', 'price', 'category', 'body')
        widgets = {
            'category': forms.Select(choices=choice_list, attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control',  'value': 'test', 'id': 'test', }),
        }

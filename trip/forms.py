from django import forms
from .models import TripPlan, CategoryTrip

choice = CategoryTrip.objects.all().values_list('name', 'name')
choice_list = []
for item in choice:
    choice_list.append(item)


class TripPlanForm(forms.ModelForm):
    class Meta:
        model = TripPlan
        fields = ('title', 'duration', 'price', 'category', 'body')
        widgets = {
            'category': forms.Select(choices=choice_list, attrs={'class': 'form-control'})
        }

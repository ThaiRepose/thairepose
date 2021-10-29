from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView , DetailView # get qurry set from database
from .models import TripPlan

def index(request):
    return render(request, "trip/index.html")

class HomeView(ListView):
    """Class to create hangle show all trip."""
    model = TripPlan
    template_name = 'trip/trip_plan.html'
    context_object_name = 'object'


class DetailView(DetailView):
    """Class to handle the detail of each trip."""
    model = TripPlan
    template_name = 'trip/trip_detail.html'
    queryset = TripPlan.objects.all()
    context_object_name = 'post'
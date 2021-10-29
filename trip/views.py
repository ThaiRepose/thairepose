from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import TripPlan


def index(request):
    """Method for link url with index template."""
    return render(request, "trip/index.html")


class HomeView(ListView):
    """Class to create handle show all trip."""

    model = TripPlan
    template_name = 'trip/trip_plan.html'
    context_object_name = 'object'


class DetailView(DetailView):
    """Class to handle the detail of each trip."""

    model = TripPlan
    template_name = 'trip/trip_detail.html'
    queryset = TripPlan.objects.all()
    context_object_name = 'post'

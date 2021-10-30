from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
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
    

class AddPost(CreateView):
    model = TripPlan
    template_name = "trip/add_blog.html"
    fields = '__all__'
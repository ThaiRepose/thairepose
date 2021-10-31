from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView
from .models import TripPlan, Review


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
    """Class to handle the create trip."""

    model = TripPlan
    template_name = "trip/add_blog.html"
    fields = '__all__'


class AddReview(CreateView):
    """Class to handle the create review."""

    model = Review
    template_name = "trip/add_review.html"
    fields = '__all__'


def LikeView(request, pk):
    """Function to user like of each commend."""
    post = get_object_or_404(Review, id=request.POST.get('commend_id'))
    post.like.add(request.user)
    return HttpResponseRedirect(reverse('trip:tripdetail', args=[str(pk)]))

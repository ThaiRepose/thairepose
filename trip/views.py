from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView
from .models import TripPlan, Review
from django.contrib.auth.decorators import login_required


def index(request):
    """Method for link url with index template."""
    return render(request, "trip/index.html")


class HomeView(ListView):
    """Class for link html of show all trip page."""

    model = TripPlan
    template_name = 'trip/trip_plan.html'
    context_object_name = 'object'


class DetailView(DetailView):
    """Class for link html of detail of eaach trip."""

    model = TripPlan
    template_name = 'trip/trip_detail.html'
    queryset = TripPlan.objects.all()
    context_object_name = 'post'


class AddPost(CreateView):
    """Class for link html of add trip page."""

    model = TripPlan
    template_name = "trip/add_blog.html"
    fields = '__all__'


class AddReview(CreateView):
    """Class for link html of add review."""

    model = Review
    template_name = "trip/add_review.html"
    fields = ('body',)

    def form_valid(self, form):
        """Auto choose current post for add comment."""
        form.instance.post_id = self.kwargs['pk']
        form.instance.name = self.request.user
        return super().form_valid(form)

@login_required
def likeview(request, pk):
    """Methid for store user like of each commend."""
    post = get_object_or_404(Review, id=request.POST.get('commend_id'))
    post.like.add(request.user)
    return HttpResponseRedirect(reverse('trip:tripdetail', args=[str(pk)]))

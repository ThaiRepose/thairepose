from django.http import HttpResponseNotFound, HttpResponseRedirect
import json
import os
from django.shortcuts import render, get_object_or_404
import requests
from dotenv import load_dotenv
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import TripPlan, Review, CategoryTrip
from .forms import TripPlanForm
from django.contrib.auth.decorators import login_required


def get_details_context(place_data: dict, api_key: str) -> dict:
    """Get context for place details page.

    Args:
        place_data: The data received from Google Cloud Platform.
        api_key: Exposed API key used to display images in website, restriction in GCP needed.

    Returns:
        context data needed for place details page.
    """
    context = {}
    if 'result' in place_data.keys():
        if 'name' in place_data['result'].keys():
            context['name'] = place_data['result']['name']
        if 'formatted_phone_number' in place_data['result'].keys():
            context['phone'] = place_data['result']['formatted_phone_number']
        if 'website' in place_data['result'].keys():
            context['website'] = place_data['result']['website']
        if 'rating' in place_data['result'].keys():
            context['rating'] = range(
                round(int(place_data['result']['rating'])))
            context['blank_rating'] = range(
                5 - round(int(place_data['result']['rating'])))
        if 'photos' in place_data['result'].keys():
            images = []
            current_photo = 0
            for data in place_data['result']['photos']:
                url = f"https://maps.googleapis.com/maps/api/place/" \
                      f"photo?maxwidth=600&photo_reference={data['photo_reference']}&key={api_key}"
                images.append(url)
                current_photo += 1
                if current_photo >= 4:
                    break
            context['images'] = images
        if 'reviews' in place_data['result'].keys():
            reviews = []
            for i in place_data['result']['reviews']:
                if i['text'] != "":
                    reviews.append({
                        'author': i['author_name'],
                        'text': i['text']
                    })
            context['reviews'] = reviews
        lat, lng = None, None
        if 'geometry' in place_data['result'].keys():
            if 'location' in place_data['result']['geometry'].keys():
                if 'lat' in place_data['result']['geometry']['location'].keys():
                    lat = place_data['result']['geometry']['location']['lat']
                if 'lng' in place_data['result']['geometry']['location'].keys():
                    lng = place_data['result']['geometry']['location']['lng']
        if lat is not None and lng is not None:
            suggestions = []
            url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/" \
                  f"json?location={lat}%2C{lng}&radius=2000&key={api_key}"
            response = requests.get(url)
            place_data = json.loads(response.content)
            for place in place_data['results'][1:]:
                if place['name'] == context['name']:
                    continue
                if 'photos' not in place.keys():
                    continue
                url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=600" \
                      f"&photo_reference={place['photos'][0]['photo_reference']}&key={api_key}"
                suggestions.append({
                    'name': place['name'],
                    'photo': url,
                    'place_id': place['place_id']
                })
            context['suggestions'] = suggestions
    return context


def index(request):
    """Render Index page."""
    return render(request, "trip/index.html")


class AllTrip(ListView):
    """Class for link html of show all trip page."""

    model = TripPlan
    template_name = 'trip/trip_plan.html'
    context_object_name = 'object'
    ordering = ['-id']


class TripDetail(DetailView):
    """Class for link html of detail of eaach trip."""

    model = TripPlan
    template_name = 'trip/trip_detail.html'
    queryset = TripPlan.objects.all()
    context_object_name = 'post'


class AddPost(CreateView):
    """Class for link html of add trip page."""

    model = TripPlan
    template_name = "trip/add_blog.html"
    form_class = TripPlanForm


class AddCategory(CreateView):
    """Class for link html of add category page."""

    model = CategoryTrip
    template_name = "trip/add_category.html"
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


class EditPost(UpdateView):
    """Class for link html of edit post."""

    model = TripPlan
    template_name = "trip/update_plan.html"
    fields = ['title', 'duration', 'price', 'body']


class DeletePost(DeleteView):
    """Class for link html of delete post."""

    model = TripPlan
    template_name = "trip/delete_plan.html"
    context_object_name = 'post'
    success_url = reverse_lazy('trip:tripplan')


@login_required
def like_view(request, pk):
    """Methid for store user like of each commend."""
    post = get_object_or_404(Review, id=request.POST.get('commend_id'))
    post.like.add(request.user)
    return HttpResponseRedirect(reverse('trip:tripdetail', args=[str(pk)]))


def place_info(request, place_id: str):
    """Render Place information page.

    Args:
        request: auto-generated by django.
        place_id: place identity defined by Google

    Returns:
        HttpRequest: Return 200 if place_id is correct, and return 404 if invalid.
    """
    load_dotenv()
    api_key = os.getenv('API_KEY')
    field = "&fields=name%2Cformatted_phone_number%2Cphoto%2Cwebsite%2Crating%2Creviews%2Cgeometry/location"
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}{field}&key={api_key}"
    response = requests.get(url)
    data = json.loads(response.content)
    if data['status'] != "OK":
        return HttpResponseNotFound(f"<h1>Response error with place_id: {place_id}</h1>")
    context = get_details_context(data, os.getenv('API_KEY'))
    return render(request, "trip/place_details.html", context)

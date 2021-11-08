from pathlib import Path
from django.http import HttpResponseNotFound, HttpResponseRedirect
import json
import os
from ast import literal_eval
from django.shortcuts import render, get_object_or_404
import requests
from src.caching.caching_gmap import APICaching
from dotenv import load_dotenv
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView
from .models import TripPlan, Review
from django.contrib.auth.decorators import login_required
import pickle
api_caching = APICaching()

def restruct_detail_context_data(context):
    """Process data for frontend

    Args:
        places: A place nearby data from google map api.

    Returns:
        context: A place data that place-list page needed.
            

    Data struct:
    [   # main place data
        {   
            # Essential key
            'place_name': <name>,
            'place_id': <place_id>,
            'photo_ref': [<photo_ref],
            'type': [],
            # other...
        }
        # sugguestion place data
        . . .
    ]
    """
    init_data = []
    main_data = {
                'place_name': context['place_name'],
                'place_id': context['place_id'],
                'photo_ref': [img for img in context['images']],
                'types': context['types'],
                'reviews': context['reviews'],
                'phone': context['phone'],
                'rating': context['rating'],
                'blank_rating': context['blank_rating']
                }
    if 'website' in context:            
        main_data["website"] = context['website']
    init_data.append(main_data)
    init_data += context['suggestions']
    return init_data

def resturct_to_place_detail(context):
    """Convert cache data to place_detail data.
        {
            "place_name": <place_name>,
            "place_id": <place_id>,
            "types": [..<types>],
            "phone": <phone_number>,
            "website": <website>,
            "rating": <rating>,
            "blank_rating": <blank_rating>,
            "images": [],
            "reviews": [],
            "suggestions": []
        }
    """
    init_data = {
                    "place_name": context[0]['place_name'],
                    "place_id": context[0]['place_id'],
                    "types": [context[0]['types']],
                    "phone": context[0]['phone'],
                    "rating": context[0]['rating'],
                    "blank_rating": context[0]['blank_rating'],
                    "images": [img for img in context[0]['photo_ref']],
                    "reviews": context[0]['reviews'],
                    "suggestions": [place for place in context[1:]]
                }
    if 'website' in context[0]:            
        init_data["website"] = context[0]['website'],
    return init_data
    


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
            context['place_name'] = place_data['result']['name']
        if 'place_id' in place_data['result'].keys():
            context['place_id'] = place_data['result']['place_id']
        if 'types' in place_data['result'].keys():
            context['types'] = place_data['result']['types']
        if 'formatted_phone_number' in place_data['result'].keys():
            context['phone'] = place_data['result']['formatted_phone_number']
        if 'website' in place_data['result'].keys():
            context['website'] = place_data['result']['website']
            print(type(place_data['result']['website']))
        if 'rating' in place_data['result'].keys():
            context['rating'] = int(place_data['result']['rating'])
            context['blank_rating'] = 5 - int(place_data['result']['rating'])
        else:
            context['rating'] = 0
            context['blank_rating'] = 0
        if 'photos' in place_data['result'].keys():
            images = []
            current_photo = 0
            for data in place_data['result']['photos']:
                img_ref = data['photo_reference']
                images.append(img_ref)
                current_photo += 1
                if current_photo >= 4:
                    break
            context['images'] = images
        else:
            context['images'] = []
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
                if place['name'] == context['place_name']:
                    continue
                if 'photos' not in place.keys():
                    continue
                img_ref = place['photos'][0]['photo_reference']
                # f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=600" \
                #       f"&photo_reference={place['photos'][0]['photo_reference']}&key={api_key}"
                suggestions.append({
                    'place_name': place['name'],
                    'photo_ref': img_ref,
                    'place_id': place['place_id']
                })
            context['suggestions'] = suggestions
            print(json.dumps(context, indent=3))
    return context



def check(context):
    name = context['place_name']
    ROOT_DIR = Path(__file__).resolve().parent.parent
    PLACE_IMG_PATH = os.path.join(ROOT_DIR,'theme','static','images','places_image')
    all_img = [f for f in os.listdir(PLACE_IMG_PATH) if os.path.isfile(os.path.join(PLACE_IMG_PATH, f))]
    for idx in range(len(context['images'])):
        if not f'{name}{idx}detailphoto.jpeg' in all_img:
            return False
    return True


def index(request):
    """Render Index page."""
    return render(request, "trip/index.html")


class AllTrip(ListView):
    """Class for link html of show all trip page."""

    model = TripPlan
    template_name = 'trip/trip_plan.html'
    context_object_name = 'object'


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
    if api_caching.get(f"{place_id}detailpage"):
        cache_data = json.loads(api_caching.get(f"{place_id}detailpage"))['cache']
    else:
        load_dotenv()
        api_key = os.getenv('API_KEY')
        field = "&fields=name%2Ctype%2Cformatted_phone_number%2Cphoto%2Cplace_id%2Cwebsite%2Crating%2Creviews%2Cgeometry/location"
        url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}{field}&key={api_key}"
        response = requests.get(url)
        data = json.loads(response.content)
        if data['status'] != "OK":
            return HttpResponseNotFound(f"<h1>Response error with place_id: {place_id}</h1>")
        context = get_details_context(data, os.getenv('API_KEY'))
        cache_data = restruct_detail_context_data(context)
        api_caching.add(f"{place_id}detailpage", json.dumps({'cache':cache_data}, indent=3).encode())
    
    context = resturct_to_place_detail(cache_data)
    context['blank_rating'] = range(round(context['blank_rating']))
    context['rating'] = range(round(context['rating']))
    check_image(context)
    return render(request, "trip/place_details.html", context)

def check_image(context):
    context['downloaded'] = check(context)
    if context['downloaded']:
        context["img_name"] = context['place_name'].replace(" ", "-")
        context["images"] = list(range(len(context["images"])))

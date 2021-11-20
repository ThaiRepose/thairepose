from django.shortcuts import render
from django.http import JsonResponse

import os
import json
import time
from .api import GoogleAPI
from threpose.settings import BASE_DIR
from src.caching.caching_gmap import APICaching

from dotenv import load_dotenv
load_dotenv()

gapi = GoogleAPI()
api_caching = APICaching()

PLACE_IMG_PATH = os.path.join(BASE_DIR, 'theme', 'static', 'images', 'places_image')


# Place List page
def get_next_page_from_token(request):  # pragma: no cover
    """Get places list data by next_page_token."""
    # Check request
    if request.method != 'POST':
        return JsonResponse({"status": "INVALID METHOD"})
    if 'token' not in request.POST:
        return JsonResponse({"status": "INVALID PAYLOAD"})
    # Get next page token from request
    token = request.POST['token']

    context = []

    # Check next_page cache
    if api_caching.get(f'{token[:30]}') is None:
        for _ in range(6):
            # Request data for 6 times, if response is not OK
            # and reached maximum, it will return empty
            data = json.loads(gapi.next_search_nearby(token))
            if data['status'] == "OK":
                context = restruct_nearby_place(data['results'])
                break
            time.sleep(0.2)
        # write cache file
        byte_context = json.dumps({"cache": context, "status": "OK"}, indent=3).encode()
        api_caching.add(f'{token[:30]}', byte_context)
        if len(context) > 0:
            return JsonResponse({"places": context, "status": "OK"})
        return JsonResponse({"places": context, "status": "NOT FOUND"})
    else:  # Have cache
        # load cache
        context = json.loads(api_caching.get(f'{token[:30]}'))
        # check place images
        context = check_downloaded_image(context['cache'])
        return JsonResponse({"places": context, "status": "OK"})


def place_list(request, *args, **kwargs):  # pragma: no cover
    """Place_list view for list place that nearby the user search input."""
    data = request.GET  # get lat and lng from url
    # Our default search type
    types = ['restaurant', 'zoo', 'tourist_attraction', 'museum', 'cafe', 'aquarium']

    lat = data['lat']
    lng = data['lng']

    # Get place cache
    if api_caching.get(f'{lat}{lng}searchresult'):
        # data exists
        data = json.loads(api_caching.get(f'{lat}{lng}searchresult'))
        context = data['cache']
        token = data['next_page_token']
    else:
        # data not exist
        context, token = get_new_context(types, lat, lng)
    context = check_downloaded_image(context)
    # get all image file name in static/images/place_image
    api_key = os.getenv('API_KEY')
    return render(request, "search/place_list.html", {'places': context, 'all_token': token, 'api_key': api_key})


# Helper function
def get_new_context(types: list, lat: int, lng: int) -> list:  # pragma: no cover
    """Cache new data and return the new data file

    Args:
        types: place type

        lat, lng: latitude and longitude of user search input for

    Returns:
        context: places nearby data
        token: next page token
    """
    token = {}
    # This create for keeping data from search nearby
    tempo_context = []
    for type in types:
        data = json.loads(gapi.search_nearby(lat, lng, type))
        if 'next_page_token' in data:
            token[type] = data['next_page_token']
        places = data['results']
        restructed_places = restruct_nearby_place(places)
        tempo_context = add_more_place(tempo_context, restructed_places)
    # Caching places nearby
    cache = {'cache': tempo_context, 'next_page_token': token}
    api_caching.add(f'{lat}{lng}searchresult', json.dumps(cache, indent=3).encode())
    # Load data from cache
    context = json.loads(api_caching.get(f'{lat}{lng}searchresult'))['cache']
    return context, token


def restruct_nearby_place(places: list) -> list:
    """Process data for frontend

    Args:
        places: A place nearby data from google map api.

    Returns:
        context: A place data that place-list page needed.

    Data struct:
    [
        {
            # Essential key
            'place_name': <name>,
            'place_id': <place_id>,
            'photo_ref': [<photo_ref],
            'types': [],
            # other...
        }
        . . .
    ]
    """
    context = []
    for place in places:
        init_place = {
            'place_name': None,
            'place_id': None,
            'photo_ref': [],
            'types': [],
        }

        if 'photos' in place:
            # Place have an image
            photo_ref = place['photos'][0]['photo_reference']
            init_place['photo_ref'].append(photo_ref)
        else:
            # Place don't have an image
            continue
        init_place['place_name'] = place['name']
        init_place['place_id'] = place['place_id']
        init_place['types'] = place['types']
        context.append(init_place)
    return context


def check_downloaded_image(context: list) -> list:
    """Check that image from static/images/place_image that is ready for frontend to display or not

    Args:
        context: place nearby data

    Returns:
        context: place nearby data with telling the image of each place were downloaded or not
    """
    # Check places_image dir that is exists
    if os.path.exists(PLACE_IMG_PATH):
        # Get image file name from static/images/places_image
        all_img_file = [f for f in os.listdir(PLACE_IMG_PATH)
                        if os.path.isfile(os.path.join(PLACE_IMG_PATH, f))]
        for place in context:
            # If place that have photo_ref imply that place have an images
            if 'photo_ref' in place:
                place_id = place['place_id']
                downloaded_img = f'{place_id}photo.jpeg' in all_img_file
                have_image = len(place['photo_ref']) == 0
                if downloaded_img or have_image:
                    place['downloaded'] = True
                else:
                    place['downloaded'] = False
    return context


def add_more_place(context: list, new: list):
    """Append places to context

    Args:
        context: total nearby palce data

        new: new data by next page tokens

    Returns:
        context: total nearby place that append
        new to is's with out duplicated place
    """
    place_exist = [place['place_id'] for place in context]
    for place in new:
        # Check that place is exists or not
        if place['place_id'] in place_exist:
            continue
        context.append(place)
    return context

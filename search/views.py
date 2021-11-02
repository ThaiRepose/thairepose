from django.shortcuts import render
import os, json
from .api import GoogleAPI
from threpose.settings import BASE_DIR
from src.caching.api_caching import APICaching
from subprocess import call
from dotenv import load_dotenv
load_dotenv()

gapi = GoogleAPI()
api_caching = APICaching()

PLACE_IMG_PATH = os.path.join(BASE_DIR,'theme','static','images','places_image')

def place_list(request, *args, **kwargs):
    data = request.GET
    type = 'restaurant'
    lat = data['lat']
    lng = data['lng']

    if api_caching.get(f'{lat}{lng}{type}searchresult'):
        places = json.loads(api_caching.get(f'{lat}{lng}{type}searchresult'))["results"]
    else: 
        places = gapi.search_nearby(lat, lng, type)
        api_caching.add(f'{lat}{lng}{type}searchresult', places)
        places = json.loads(api_caching.get(f'{lat}{lng}{type}searchresult'))["results"]
        
    all_img_file = [f for f in os.listdir(PLACE_IMG_PATH) if os.path.isfile(os.path.join(PLACE_IMG_PATH, f))]
    
    for place in places:
        place_id = place['place_id']
        if f'{place_id}photo.jpeg' in all_img_file:
            place['have_photo'] = True
        else:
            place['have_photo'] = False
    return render(request, "search/place_list.html", {'places':places})

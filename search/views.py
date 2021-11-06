from django.shortcuts import render
import os, json
from .api import GoogleAPI
from threpose.settings import BASE_DIR
from src.caching.caching_gmap import APICaching
from subprocess import call
import time
from dotenv import load_dotenv
load_dotenv()

gapi = GoogleAPI()
api_caching = APICaching()

PLACE_IMG_PATH = os.path.join(BASE_DIR,'theme','static','images','places_image')

def restruct_nearby_place(places):
    """
    data struct
    -----------
    [
        {   
            # Essential key
            'place_name': <name>,
            'place_id': <place_id>,
            'photo_ref': [<photo_ref],
            'type': [],
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
                        'type': [],
                     }
        init_place['place_name'] = place['name']
        init_place['place_id'] = place['place_id']
        if 'photos' in place:
            init_place['photo_ref'].append(place['photos'][0]['photo_reference'])
            init_place['name_img'] = str(place['name'].replace(' ', '-'))
        init_place['type'] = place['types']
        context.append(init_place)
    return context

def add_more_place(context, new):
    place_exist = [place['place_id'] for place in context]
    for place in new:
        if place['place_id'] in place_exist:
            continue
        context.append(place)
    return context

def place_list(request, *args, **kwargs):
    data = request.GET
    types = ['restaurant', 'shopping_mall', 'supermarket', 'zoo', 'tourist_attraction','museum', 'cafe']
    lat = data['lat']
    lng = data['lng']

    if api_caching.get(f'{lat}{lng}searchresult'):
        context = json.loads(api_caching.get(f'{lat}{lng}searchresult'))['cache']
        print(len(context))
    else:
        tempo_context = []
        for type in types:
            data = json.loads(gapi.search_nearby(lat, lng, type))
            places = data['results']
            restructed_places = restruct_nearby_place(places)
            tempo_context = add_more_place(tempo_context, restructed_places)  
        api_caching.add(f'{lat}{lng}searchresult', json.dumps({'cache':tempo_context}, indent=3).encode())
        context = json.loads(api_caching.get(f'{lat}{lng}searchresult'))['cache']
    all_img_file = [f for f in os.listdir(PLACE_IMG_PATH) if os.path.isfile(os.path.join(PLACE_IMG_PATH, f))]
    
    for place in context:
        if 'name_img' in place:
            place_name = place['name_img']
            if f'{place_name}photo.jpeg' in all_img_file or len(place['photo_ref']) == 0:
                img_downloaded = True
            else:
                img_downloaded = False
    return render(request, "search/place_list.html", {'places': context, 'img_downloaded': img_downloaded})

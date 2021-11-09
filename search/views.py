from django.shortcuts import render
from django.http import JsonResponse
import os, json

from requests import api
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
            init_place['name_img'] = str(place['name'].replace(' ', '-').replace("|","").replace(':', "_").replace('"',"").replace('#',""))
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
    types = ['restaurant', 'shopping_mall', 'supermarket', 'zoo', 'tourist_attraction', 'museum', 'cafe', 'aquarium']
    lat = data['lat']
    lng = data['lng']
    token = {}
    if api_caching.get(f'{lat}{lng}searchresult'):
        data = json.loads(api_caching.get(f'{lat}{lng}searchresult'))
        context = data['cache']
        token = data['next_page_token']
    else:
        tempo_context = []
        for type in types:
            data = json.loads(gapi.search_nearby(lat, lng, type))
            if 'next_page_token' in data:
                token[type] = data['next_page_token']
            places = data['results']
            restructed_places = restruct_nearby_place(places)
            tempo_context = add_more_place(tempo_context, restructed_places)  
        api_caching.add(f'{lat}{lng}searchresult', json.dumps({'cache':tempo_context, 'next_page_token':token}, indent=3).encode())
        context = json.loads(api_caching.get(f'{lat}{lng}searchresult'))['cache']
    all_img_file = [f for f in os.listdir(PLACE_IMG_PATH) if os.path.isfile(os.path.join(PLACE_IMG_PATH, f))]
    
    for place in context:
        if 'name_img' in place:
            place_name = place['name_img']
            if f'{place_name}photo.jpeg' in all_img_file or len(place['photo_ref']) == 0:
                img_downloaded = True
            else:
                img_downloaded = False

    api_key = os.getenv('API_KEY')
    return render(request, "search/place_list.html", {'places': context, 'img_downloaded': img_downloaded, 'all_token': token, 'api_key': api_key})


def get_next_page_from_token(request):
    """Get places list data by next_page_token."""
    if request.method != 'POST':
        return JsonResponse({"status": "INVALID METHOD"})
    if 'token' not in request.POST:
        return JsonResponse({"STATUS": "INVALID PAYLOAD"})
    token = request.POST['token']
    context = []
    if api_caching.get(f'{token[:30]}') is None:
        for _ in range(6):  # Request data for 6 times, if response is not OK and reached maximum, it will return empty
            data = json.loads(gapi.next_search_nearby(token))
            if data['status'] == "OK":
                context = restruct_nearby_place(data['results'])
                break
            time.sleep(0.2)
        byte_context = json.dumps({"cache": context, "status": "OK"}, indent=3).encode()
        api_caching.add(f'{token[:30]}', byte_context)
        if len(context) > 0:
            return JsonResponse({"places": context, "status": "OK"})
        return JsonResponse({"places": context, "status": "NOT FOUND"})
    else:
        context = json.loads(api_caching.get(f'{token[:30]}'))
        
        return JsonResponse({"places": context['cache'], "status": "OK"})

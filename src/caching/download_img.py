from os import listdir
from os.path import isfile, join
from pathlib import Path
import json, os
import requests
from api_caching import APICaching
import datetime


api_caching = APICaching()



ROOT_DIR = Path(__file__).resolve().parent.parent.parent
PLACE_IMG_PATH = os.path.join(ROOT_DIR,'theme','static','images','places_image')


while True:
    all_cache_file = [f for f in listdir(join(ROOT_DIR,'__cache__')) if isfile(join(join(ROOT_DIR,'__cache__'), f))]
    if not os.path.exists(PLACE_IMG_PATH):
        os.mkdir(os.path.join(ROOT_DIR,'theme','static','images','places_image'))
    all_img = [f for f in listdir(PLACE_IMG_PATH) if isfile(join(PLACE_IMG_PATH, f))]
    for file in all_cache_file:
        if not ('searchresult' in file):
            continue
        data = json.loads(api_caching.get(f'{file[:-6]}'))["results"]
        # print(data)
        for sup_data in data:
            place_id = sup_data['place_id']
            if not ('photos' in sup_data) or (f'{place_id}photo.jpeg' in all_img):
                continue
            x = datetime.datetime.now()
            print(f"[{str(x)}] call")
            photo_ref = sup_data['photos'][0]['photo_reference']
            url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_ref}&key=AIzaSyBxO1khE-LHn5Z5U2SWpA36D4nKqoWzNRg"
            payload={}
            headers = {}
            response = requests.request("GET", url, headers=headers, data=payload)
            new_file = open(os.path.join(PLACE_IMG_PATH, f'{place_id}photo.jpeg'), 'wb') 
            new_file.write(response.content) 

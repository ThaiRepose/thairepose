from os import listdir
from os.path import isfile, join
from pathlib import Path
import json, os
import requests
from caching_gmap import APICaching
import datetime
import click
import pathlib

api_caching = APICaching()
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
PLACE_IMG_PATH = os.path.join(ROOT_DIR,'theme','static','images','places_image')


def write_img_from_gmap_api(key, photo_ref):
    api_key = os.getenv('API_KEY')
    url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=600&photo_reference={photo_ref}&key={api_key}"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    new_file = open(os.path.join(PLACE_IMG_PATH, f'{key}photo.jpeg'), 'wb') 
    new_file.write(response.content)
    x = datetime.datetime.now()
    print('[' + x.strftime("%d:%m:%y %X")+ ']' + f" {key}photo.jpeg has been downloaded")

def run():
    while True:
        all_cache_file = [f for f in listdir(join(ROOT_DIR,'__cache__')) if isfile(join(join(ROOT_DIR,'__cache__'), f))]
        if not os.path.exists(PLACE_IMG_PATH):
            os.mkdir(PLACE_IMG_PATH)

        all_img = [f for f in listdir(PLACE_IMG_PATH) if isfile(join(PLACE_IMG_PATH, f))]
        now = datetime.datetime.now()
        if not os.path.exists(os.path.join(BASE_DIR,'expireTable.json')):
            json_init = {}
            with open(os.path.join(BASE_DIR,'expireTable.json'), 'w') as json_file:
                json.dump(json_init, json_file)
        with open(os.path.join(BASE_DIR,'expireTable.json')) as json_file:
            json_decoded = json.load(json_file)
        
        for file in all_cache_file:
            cache = json.loads(api_caching.get(file[:-6]))['cache']
            for supdata in cache:
                name = supdata['place_name'].replace(' ', '-').replace("|","").replace(':', "_").replace('"',"").replace('#',"")
                if f'{name}photo.jpeg' in all_img:
                    continue
                
                if len(supdata['photo_ref']) == 1:
                    write_img_from_gmap_api(f'{name}', supdata['photo_ref'][0])
                else:
                    for idx in range(len(supdata['photo_ref'])):
                        write_img_from_gmap_api(f'{name}{idx}', supdata['photo_ref'][idx])
                        

@click.group()
def cli():
    pass

@click.command()
def start():
    print("""
    ████████╗ ██████╗░ ░░░░░░ ░█████╗░ ░█████╗░ ░█████╗░ ██╗░░██╗ ██╗ ███╗░░██╗ ░██████╗░
    ╚══██╔══╝ ██╔══██╗ ░░░░░░ ██╔══██╗ ██╔══██╗ ██╔══██╗ ██║░░██║ ██║ ████╗░██║ ██╔════╝░
    ░░░██║░░░ ██████╔╝ █████╗ ██║░░╚═╝ ███████║ ██║░░╚═╝ ███████║ ██║ ██╔██╗██║ ██║░░██╗░
    ░░░██║░░░ ██╔══██╗ ╚════╝ ██║░░██╗ ██╔══██║ ██║░░██╗ ██╔══██║ ██║ ██║╚████║ ██║░░╚██╗
    ░░░██║░░░ ██║░░██║ ░░░░░░ ╚█████╔╝ ██╔══██║ ╚█████╔╝ ██║░░██║ ██║ ██║░╚███║ ╚██████╔╝
    ░░░╚═╝░░░ ╚═╝░░╚═╝ ░░░░░░ ░╚════╝░ ╚═╝░░╚═╝ ░╚════╝░ ╚═╝░░╚═╝ ╚═╝ ╚═╝░░╚══╝╝░╚═════╝░
    version 0.1.0 dev.
    """) 
    run()


cli.add_command(start)
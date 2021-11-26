"""
TR-CACHING system is a caching system or auto
download image system you can call it what you want
It will read a cache file that have a 'cache' in it
and element in 'cache' that have photo reference
it will autometic download image by photo reference.

# Installation
`pip install --editable ~/caching/.`

# TR_CACHING CLI
- `tr-caching start`: run auto download image.

..Author Vitvara Varavithya
This is my first time writting something like this, it will have
a lot of bug that I can not find it all by my self if you find it contact me or
you can open issue on our repository to let me know. And If you have an idea to
solve it or have a better way to do it fork and make a pull request and request me to be
your reviewer I will review it as fast as I can.
GitHub `vitvara`

"""

import json
import os
import requests
import datetime
import click
from os import listdir
from os.path import isfile
from os.path import join
from pathlib import Path
from caching_gmap import APICaching

from decouple import config

api_caching = APICaching()

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
PLACE_IMG_PATH = os.path.join(ROOT_DIR, 'media', 'places_image')


def write_img_from_gmap_api(key: str, photo_ref: str):
    """Write image by photo ref

    Args:
        key: name of the image file

        photo_ref: photo reference from gmap api
    """
    api_key = config('BACKEND_API_KEY')
    url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=600&photo_reference={photo_ref}&key={api_key}"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    new_file = open(os.path.join(PLACE_IMG_PATH, f'{key}photo.jpeg'), 'wb')
    new_file.write(response.content)
    x = datetime.datetime.now()
    print('[' + x.strftime("%d:%m:%y %X") + ']' + f" {key}photo.jpeg has been downloaded")


def download_img_by_photo_ref():
    """
    List all photo ref that need to download and make the place_id to key and send it
    to write_img_from_gmap_api
    """
    # get cache file name
    all_cache_file = [f for f in listdir(join(ROOT_DIR, '__cache__')) if isfile(join(join(ROOT_DIR, '__cache__'), f))]
    # get image filename
    all_img = [f for f in listdir(PLACE_IMG_PATH) if isfile(join(PLACE_IMG_PATH, f))]
    for file in all_cache_file:
        # read cache
        cache = json.loads(api_caching.get(file[:-6]))['cache']
        for supdata in cache:
            name = supdata['place_id']
            max = len(supdata['photo_ref'])
            # have one image
            if only_one_image(supdata, max) and (f'{name}photo.jpeg' not in all_img):
                if isinstance(supdata['photo_ref'], str):
                    write_img_from_gmap_api(f'{name}', supdata['photo_ref'])
                else:
                    write_img_from_gmap_api(f'{name}', supdata['photo_ref'][0])
            # have more than one image
            elif not (f'{name}_{max-1}photo.jpeg' in all_img) and not (only_one_image(supdata, max)):
                for idx in range(max):
                    if f'{name}_{idx}photo.jpeg' in all_img:
                        continue
                    write_img_from_gmap_api(f'{name}_{idx}', supdata['photo_ref'][idx])


def only_one_image(supdata, max):
    """Place have one image"""
    return max == 1 or isinstance(supdata['photo_ref'], str)


def run():
    """run auto download image"""
    while True:
        if not os.path.exists(PLACE_IMG_PATH):
            os.mkdir(PLACE_IMG_PATH)
        if not os.path.exists(os.path.join(BASE_DIR, 'expireTable.json')):
            json_init = {}
            with open(os.path.join(BASE_DIR, 'expireTable.json'), 'w') as json_file:
                json.dump(json_init, json_file)
        # with open(os.path.join(BASE_DIR, 'expireTable.json')) as json_file:
        #     json_decoded = json.load(json_file)
        download_img_by_photo_ref()


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

import os
import os.path
import json
from pathlib import Path


class APICaching:
    """Save, delete, get, and expire data you can keep every data that you want but!!
    every data that you keep must be bytes-like object.

    Data structure:
    {
        'cache':[],
        # * you can keep any thing here * #
    }

    'cache' this key made for data that have a photo referance
    if you only want to keep data that not have a photo reference
    you can ignore it. But if you want to download an image you
    need to put it on the 'cache'.

    In 'cache' its keep a list of data ex. `'cache': [{'place_id': 123456, 'photo_ref':[1,2,3,4]}]`
    In this example if you are runing the `tr-caching start` command
    it will autometic donwload image from google map api
    with photo referance is 1, 2, 3, 4. And if that place don't have a image
    you can leave it there ex. `'cache': [{'place_id': 123456}]`

    How to use:
        # * Avalible command * #
        - add: add cache data
            Args:
                key: str
                data: bytes

        - get: get data from cache by key
            Args:
                key: str
            Returns:
                data: bytes
                    data read from cache file

        - delete: delete cache file by key
            Args:
                key: str

    """
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent
    BASE_DIR = Path(__file__).resolve().parent

    def __init__(self):
        if not os.path.exists(os.path.join(self.ROOT_DIR, '__cache__')):
            os.mkdir(os.path.join(self.ROOT_DIR, '__cache__'))

    def add(self, key: str, data: bytes):
        new_file = open(os.path.join(self.ROOT_DIR, '__cache__', f'{key}.cache'), 'wb')
        new_file.write(data)

    def get(self, key):
        if os.path.exists(os.path.join(self.ROOT_DIR, '__cache__', f'{key}.cache')):
            file = open(os.path.join(self.ROOT_DIR, '__cache__', f'{key}.cache'), "rb")
            data = file.read()
            file.close()
            return data

    def delete(self, key):
        if os.path.exists(os.path.join(self.ROOT_DIR, '__cache__', f'{key}.cache')):
            os.remove(os.path.join(self.ROOT_DIR, '__cache__', f'{key}.cache'))
            print("Delete successfully")
            return True
        return False

    def expire(self, key, time_hour):
        if not os.path.exists(os.path.join(self.BASE_DIR, 'expireTable.json')):
            json_decoded = {}
        else:
            with open(os.path.join(self.BASE_DIR, 'expireTable.json')) as json_file:
                json_decoded = json.load(json_file)

        json_decoded[key] = time_hour

        with open(os.path.join(self.BASE_DIR, 'expireTable.json'), 'w') as json_file:
            json.dump(json_decoded, json_file)

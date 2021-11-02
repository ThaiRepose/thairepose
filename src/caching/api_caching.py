import os, requests, sys
from pathlib import Path

class APICaching:

    ROOT_DIR = Path(__file__).resolve().parent.parent.parent

    def __init__(self):
        
        if not os.path.exists(os.path.join(self.ROOT_DIR,'__cache__')):
            os.mkdir(os.path.join(self.ROOT_DIR,'__cache__'))

    def add(self, key, data):
        new_file = open(os.path.join(self.ROOT_DIR,'__cache__', f'{key}.cache'), 'wb')   
        new_file.write(data) 

    def set():
        pass

    def get(self, key):
        if os.path.exists(os.path.join(self.ROOT_DIR,'__cache__', f'{key}.cache')):
            file = open(os.path.join(self.ROOT_DIR,'__cache__', f'{key}.cache'), "rb")
            data = file.read()
            file.close()
            return data
    

    def delete(self, key):
        if os.path.exists(os.path.join(self.ROOT_DIR,'__cache__', f'{key}.cache')):
            os.remove(os.path.join(self.ROOT_DIR,'__cache__', f'{key}.cache'))
            return True
        return False

    def expire():
        pass
    
lat = 13.7564231
lng = 100.5016315
api_key = 'AIzaSyBxO1khE-LHn5Z5U2SWpA36D4nKqoWzNRg'
type = 'museum'
# url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=Aap_uEDh-jrj1nxtU_L8jB7kESiWkazjvNN2wxg8ut8ObvTjdXFQVY4ATiotz3LMg9GbUrOSWm6wqSq_Xv4fRGvUqDRUK6Hf-rT29EntrExIZ9vmkTKCMCjaAhs44XYMfWXKzS2x9j_yR7r3vlCc4ox9dzTqY9WiH_2XDxgqDkaMfokrf7UO&key=AIzaSyBxO1khE-LHn5Z5U2SWpA36D4nKqoWzNRg"
# payload={}
# headers = {}
# response = requests.request("GET", url, headers=headers, data=payload)
a = APICaching()
# a.add('mykey', response.content)

# url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat}%2C{lng}&radius=5000&type={type}&key={api_key}"
# payload={}
# headers = {}
# response = requests.request("GET", url, headers=headers, data=payload)
# print(response.content)
# a.add(f'{lat}{lng}{type}', response.content)
a.delete('mykey1')
import requests
import os
import urllib.parse
from dotenv import load_dotenv
load_dotenv()
import requests
import json

class GoogleAPI:

    api_key = os.getenv("API_KEY")

    def auto_complete_search_box(self, keyword):
        payload={}
        headers = {}
        url_encode_keyword = urllib.parse.quote(keyword)
        url = f"https://maps.googleapis.com/maps/api/place/queryautocomplete/json?input={url_encode_keyword}&key={self.api_key}"
        response = requests.request("GET", url, headers=headers, data=payload)
        return response.text

    def search_nearby(self,lat,lng, type):
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat}%2C{lng}&radius=5000&type=restaurant&key={self.api_key}"
        payload={}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        return json.loads(response.text)
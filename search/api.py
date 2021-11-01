import requests
import os
import urllib.parse
from dotenv import load_dotenv
load_dotenv()
import json

class GoogleAPI:

    api_key = os.getenv("API_KEY")

    def search_nearby(self,lat,lng, type):
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat}%2C{lng}&radius=5000&type={type}&key={self.api_key}"
        payload={}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        return response.content

    
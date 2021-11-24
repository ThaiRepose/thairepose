import os
import urllib.parse
import requests
import json
import time
from decouple import config


class GoogleAPI:

    api_key = config("BACKEND_API_KEY")

    def search_nearby(self, lat, lng, type):
        """Call search nearby place from google map API.

        Args:
            lat: float or str
                latitude from place_list URL
            lng: float or str
                lngtitude frin place_list URL
            type: str
            # ! You can't choose more than one type. ! #
                Google place type.

        Returns:
            response.content: bytes
                A response content in form of JSON.
        """
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat}"\
            f"%2C{lng}&radius=1500&type={type}&key={self.api_key}"
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        return response.content

    def next_search_nearby(self, token: str):
        """Call search nearby next page from google map API.

        Args:
            token: next_page_token from google map api search nearby places.

        Returns:
            response.content: next place nearby page data.
        """
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={token}&key={self.api_key}"
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        return response.content

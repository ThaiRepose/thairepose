from django.shortcuts import render
import json
from .api import GoogleAPI

gapi = GoogleAPI()

def home(request):
    
    return render(request, "search/home.html")

def search(request, *args, **kwargs):
    data = request.GET
    places = gapi.search_nearby(data['lat'], data['lng'], 'restaurant')
    places = places['results']
    return render(request, "search/detail.html", {'places':places})

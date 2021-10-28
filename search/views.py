from django.shortcuts import render
import json
from .api import GoogleAPI

gapi = GoogleAPI()
# from .api import AutoComplete

# auto_complete = AutoComplete()

# Create your views here.
def home(request):
    
    return render(request, "search/home.html")

def search(request, *args, **kwargs):
    data = request.GET
    places = gapi.search_nearby(data['lat'], data['lng'], 'restaurant')
    places = places['results']
    return render(request, "search/detail.html", {'places':places})

# {'geometry': {
#     'location': {'lat': 13.7588899, 'lng': 100.5650479}, 
#     'viewport': {
#         'northeast': {'lat': 13.7602673802915, 'lng': 100.5662536802915}, 
#         'southwest': {'lat': 13.7575694197085, 'lng': 100.5635557197085}}}, 
# 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/restaurant-71.png', 
# 'icon_background_color': '#FF9E67', 
# 'icon_mask_base_uri': 'https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet', 
# 'name': "McDonald's - Fortune Town branch", 
# 'opening_hours': {'open_now': True}, 
# 'photos': [{'height': 3024, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/111590699277910523360">Aniruth Panudomlak</a>'], 
#             'photo_reference': 'Aap_uECu0OthPrpyaA1cU---CU440-IOR-aBveXtg7sZ19Lz1xESyx8hAUnXSl2ZVxQIAEHQ7AXmbr_qtmE3wvk48TzBUWbz5ZjPQisWJPUdVj_Y28wanFmGWhB07HngTd-LmtlV5Nzim27aSMsdTxAj2W7z78UUX2gpjMl5S_PwiKEDhCI0', 'width': 4032}]
# }
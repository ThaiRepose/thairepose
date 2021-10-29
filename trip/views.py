import json
import os
from django.shortcuts import render
import requests
from dotenv import load_dotenv


def get_details_context(place_data: dict, api_key: str) -> dict:
    """Get context for place details page.

    Args:
        place_data: The data received from Google Cloud Platform.
        api_key: Exposed API key used to display images in website, restriction in GCP needed.

    Returns:
        context data needed for place details page.
    """
    context = {
        'name': place_data['result']['name']
    }
    try:
        context['phone'] = place_data['result']['formatted_phone_number']
    except Exception as error:
        print("No phone number provided.\nError Message:", error)
    try:
        context['website'] = place_data['result']['website']
    except Exception as error:
        print("No website provided.\nError Message:", error)
    try:
        context['rating'] = range(round(int(place_data['result']['rating'])))
        context['blank_rating'] = range(5 - round(int(place_data['result']['rating'])))
    except Exception as error:
        print("No rating provided.\nError Message:", error)
    try:
        images = []
        current_photo = 0
        for data in place_data['result']['photos']:
            url = f"https://maps.googleapis.com/maps/api/place/" \
                  f"photo?maxwidth=600&photo_reference={data['photo_reference']}&key={api_key}"
            images.append(url)
            current_photo += 1
            if current_photo >= 4:
                break
        context['images'] = images
    except Exception as error:
        print("No image provided.\nError Message:", error)
    try:
        reviews = []
        for i in place_data['result']['reviews']:
            if i['text'] != "":
                reviews.append({
                    'author': i['author_name'],
                    'text': i['text']
                })
        context['reviews'] = reviews
    except Exception as error:
        print("Cannot get reviews.\nError Message:", error)
    lat = place_data['result']['geometry']['location']['lat']
    lng = place_data['result']['geometry']['location']['lng']
    suggestions = []
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/" \
          f"json?location={lat}%2C{lng}&radius=1000&key={api_key}"
    response = requests.get(url)
    place_data = json.loads(response.content)
    for place in place_data['results'][1:]:
        if place['name'] == context['name']:
            continue
        try:
            url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=600" \
                  f"&photo_reference={place['photos'][0]['photo_reference']}&key={api_key}"
            suggestions.append({
                'name': place['name'],
                'photo': url,
                'place_id': place['place_id']
            })
        except Exception as error:
            print(f"No photo for {place['name']}.\nError Message:", error)
    context['suggestions'] = suggestions
    return context


# Create your views here.
def index(request):
    """Render Index page."""
    return render(request, "trip/index.html")


def place_info(request, place_id):
    """Render Place information page."""
    load_dotenv()
    api_key = os.getenv('FRONTEND_API_KEY')
    field = "&fields=name%2Cformatted_phone_number%2Cphoto%2Cwebsite%2Crating%2Creviews%2Cgeometry/location"
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}{field}&key={api_key}"
    response = requests.get(url)
    data = json.loads(response.content)
    if data['status'] != "OK":
        return render(request, "trip/place_details.html", {"err_msg": "Place not found."})
    context = get_details_context(data, api_key)
    return render(request, "trip/place_details.html", context)

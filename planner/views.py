import json
import os
from collections import defaultdict
from datetime import datetime

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from dotenv import load_dotenv

from .models import Plan, Place, MAX_PLACES_PER_DAY

load_dotenv()


@login_required(login_url='/accounts/login/')
def planner_list(request):
    """Render a page showing plan organized before created by this user."""
    user = request.user
    author_plans = Plan.objects.filter(author=user).order_by('-last_modified')
    editor_plans = Plan.objects.filter(editor__user=user).order_by('-last_modified')
    plans = author_plans | editor_plans
    return render(request, "planner/trip_planner_list.html", {"plans": plans})


@login_required(login_url='/accounts/login/')
def create_planner(request):
    """Create a new planner and redirect to new planner page."""
    user = request.user
    plan = Plan.objects.create(author=user)
    plan.save()
    return HttpResponseRedirect(reverse('planner:edit_plan', args=[plan.id], ))


@login_required
def delete_planner(request, planner_id: int):
    """Delete the planner and redirect to planner list page.

    Args:
        request: Request headers from browser.
        planner_id: Primary key of selected planner.
    """
    user = request.user
    try:
        plan = Plan.objects.get(pk=planner_id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('planner:index'))
    edit_role = plan.editor_set.filter(user=user)
    is_editor = len(edit_role) > 0
    if plan.author == user:
        plan.delete()
    elif is_editor:
        edit_role.delete()
    return HttpResponseRedirect(reverse('planner:index'))


def edit_planner(request, planner_id: int):
    """Render trip planner page as editor.

    Args:
        request: Request headers from browser.
        planner_id: Primary key of selected planner.
    """
    plan_detail = get_object_or_404(Plan, pk=planner_id)
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('planner:view_plan', args=[planner_id], ))
    user = request.user
    if not plan_detail.is_editable(user):
        return HttpResponseRedirect(reverse('planner:view_plan', args=[planner_id], ))
    is_publish = 'On' if plan_detail.status else 'Off'
    return render(request, "planner/edit_planner.html", {'api_key': os.getenv('API_KEY'),
                                                         'details': plan_detail,
                                                         'is_publish': is_publish})


def view_planner(request, planner_id: int):
    """Render trip planner page as viewer.

    Args:
        request: Request headers from browser.
        planner_id: Primary key of selected planner.
    """
    plan_detail = get_object_or_404(Plan, pk=planner_id)
    places = defaultdict(list)
    # Check permission
    if request.user.is_authenticated:
        user = request.user
    else:
        user = None
    if not plan_detail.is_viewable(user):
        return HttpResponseNotFound("You need permission.")
    for place in plan_detail.place_set.all():
        places[place.day].append({
            "place_name": place.place_name,
            "place_vicinity": place.place_vicinity,
            "place_id": place.place_id,
            "arrival_time": place.arrival_time,
            "departure_time": place.departure_time
        })
    places = dict(places)
    return render(request, "planner/view_planner.html", {"details": plan_detail, "places": places})


@require_http_methods(["POST"])
def edit_planner_backend(request):
    """Edit planner details in Backend."""
    planner_id = request.POST['planner_id']
    plan = get_object_or_404(Plan, pk=planner_id)
    if 'name' in request.POST:
        plan.name = request.POST['name']
    if 'days' in request.POST:
        plan.days = request.POST['days']
    if 'publish' in request.POST:
        plan.status = request.POST['publish']
    if 'addPlace' in request.POST:
        place_data = json.loads(request.POST['addPlace'])
        add_new_place(place_data, plan)
    if 'delPlace' in request.POST:
        item = json.loads(request.POST['delplace'])
        response = delete_place(plan, item)
        if response['status'] != "OK":
            return JsonResponse(response)
    if 'moveUp' in request.POST:
        item = json.loads(request.POST['moveUp'])
        response = move_place_up(plan, item)
        if response['status'] != "OK":
            return JsonResponse(response)
    if 'moveDown' in request.POST:
        item = json.loads(request.POST['moveDown'])
        response = move_place_down(plan, item)
        if response['status'] != "OK":
            return JsonResponse(response)
    if 'changeTime' in request.POST:
        items = json.loads(request.POST['changeTime'])
        change_time(plan, items)
    plan.save()
    return JsonResponse({"status": "OK"})


def change_time(plan: Plan, items: dict):
    """Change arrival and departure time for each place in the plan.

    Args:
        plan: plan object selected to modify the place times.
        items: modify information received from POST method.
    """
    for place in items:
        if place['arrival'] != "":
            arrival = datetime.time(datetime.strptime(place['arrival'], '%H:%M'))
        else:
            arrival = None
        departure = datetime.time(datetime.strptime(place['departure'], '%H:%M'))
        try:
            selected_place = plan.place_set.get(place_id=place['place_id'], day=place['day'],
                                                sequence=place['sequence'])
        except ObjectDoesNotExist:
            continue
        selected_place.arrival_time = arrival
        selected_place.departure_time = departure
        selected_place.save()


def move_place_down(plan: Plan, item: dict) -> dict:
    """Move place sequence to the next.

    Args:
        plan: plan object selected to modify the place sequence.
        item: modify information received from POST method.

    Returns:
        status for implementing.
    """
    try:
        current_place = plan.place_set.get(day=item['day'], sequence=item['sequence'])
    except ObjectDoesNotExist:
        return {"status": "Place not found."}
    if item['day_moved']:
        place_destination = plan.place_set.filter(day=item['day_destination'])
        if place_destination.count() >= MAX_PLACES_PER_DAY:
            return {"status": f"Day {item['day']} exceeded limit places per day."}
        place_destination.update(sequence=F('sequence') + 1)
        current_place.sequence = 1
        current_place.day = item['day_destination']
    else:
        try:
            place_destination = plan.place_set.get(day=item['day'],
                                                   sequence=item['sequence'] + 1)
        except ObjectDoesNotExist:
            return {"status": "Place not found."}
        place_destination.sequence -= 1
        current_place.sequence += 1
        place_destination.save()
    current_place.save()
    return {"status": "OK"}


def move_place_up(plan: Plan, item: dict) -> dict:
    """Move place sequence to the previous.

    Args:
        plan: plan object selected to modify the place sequence.
        item: modify information received from POST method.

    Returns:
        status for implementing.
    """
    try:
        current_place = plan.place_set.get(day=item['day'], sequence=item['sequence'])
    except ObjectDoesNotExist:
        return {"status": "Place not found."}
    if item['day_moved']:
        place_destination = plan.place_set.filter(day=item['day_destination'])
        if place_destination.count() >= MAX_PLACES_PER_DAY:
            return {"status": f"Day {item['day']} exceeded limit places per day."}
        current_place.sequence = place_destination.count() + 1
        current_place.day = item['day_destination']
    else:
        try:
            place_destination = plan.place_set.get(day=item['day'],
                                                   sequence=item['sequence'] - 1)
        except ObjectDoesNotExist:
            return {"status": "Place not found."}
        place_destination.sequence += 1
        current_place.sequence -= 1
        place_destination.save()
    current_place.save()
    return {"status": "OK"}


def delete_place(plan: Plan, item: dict) -> dict:
    """Remove place from plan.

    Args:
        plan: plan object selected to delete the place.
        item: modify information received from POST method.

    Returns:
        status for implementing.
    """
    try:
        place = plan.place_set.get(day=item['day'],
                                   sequence=item['sequence'],
                                   place_id=item['place_id'])
    except ObjectDoesNotExist:
        return {"status": "Place not found."}
    places_next = plan.place_set.filter(day=item['day'], sequence__gt=item['sequence'])
    places_next.update(sequence=F('sequence') - 1)
    place.delete()
    return {"status": "OK"}


def add_new_place(place_data: dict, plan: Plan):
    """Add a new place in selected plan.

    Args:
        place_data: place information to add a new one.
        plan: plan that the place will be added to.
    """
    sequence = plan.place_set.filter(day=place_data['day']).count() + 1
    if place_data['arrival_time'] == "":
        arrival_time = None
    else:
        arrival_time = datetime.time(datetime.strptime(place_data['arrival_time'], '%H:%M'))
    if place_data['departure_time'] == "":
        departure_time = None
    else:
        departure_time = datetime.time(
            datetime.strptime(
                place_data['departure_time'], '%H:%M'))
    place = Place(day=place_data['day'],
                  sequence=sequence,
                  place_id=place_data['place_id'],
                  place_name=place_data['place_name'],
                  place_vicinity=place_data['place_vicinity'],
                  arrival_time=arrival_time,
                  departure_time=departure_time,
                  plan=plan)
    place.save()


def get_direction(places: list) -> dict:
    """Get direction time from Google Maps Platform including order suggestion.

    Args:
        places: places to get direction time ordered by index in the list. (Maximum length: 25)

    Returns:
        Details including places and route in each place to next place.
    """
    api_key = os.getenv("API_KEY")
    waypoints = ""
    if len(places) > 2:
        waypoints = "&waypoints=place_id:"
        waypoints += '|place_id:'.join(places[1:-1])
    # Concatenate url to get request url
    url = f"https://maps.googleapis.com/maps/api/directions/json?&origin=place_id:{places[0]}" \
          f"&destination=place_id:{places[-1]}" \
          f"{waypoints}" \
          f"&key={api_key}"
    response = requests.get(url)
    data = json.loads(response.text)
    return data


@login_required(login_url='/accounts/login/')
@require_http_methods(["POST"])
def get_travel_time(request) -> JsonResponse:
    """Get How long does it takes between places receiving POST method as a list of place id.

    POST params:
        places: list of places_id that will be calculated the direction
        ordered by items order in the list.
    """
    places = json.loads(request.POST['places'])
    if len(places) > 25:
        return JsonResponse({"status": "TOO MANY PLACES"})
    if len(places) <= 1:
        return JsonResponse({"status": "NOT ENOUGH PLACE"})
    data = get_direction(places)
    return JsonResponse(data)

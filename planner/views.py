from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from .models import Plan
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()


def edit_planner(request, planner_id):
    """Render trip planner page as editor."""
    plan_detail = get_object_or_404(Plan, pk=planner_id)
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('planner:view_plan', args=[planner_id],))
    is_editable = plan_detail.author == request.user or (len(plan_detail.editor_set.filter(user=request.user)) > 0)
    return render(request, "planner/edit_planner.html", {'api_key': os.getenv('API_KEY'),
                                                         'details': plan_detail,
                                                         'editable': is_editable})


def view_planner(request, planner_id):
    """Render trip planner page as viewer."""
    plan_detail = get_object_or_404(Plan, pk=planner_id)
    return render(request, "planner/view_planner.html", {"details": plan_detail})


def edit_planner_backend(request):
    """Edit planner details in Backend."""
    planner_id = request.POST['planner_id']
    print(request.POST)
    plan = get_object_or_404(Plan, pk=planner_id)
    if 'name' in request.POST:
        plan.name = request.POST['name']
    plan.save()
    return JsonResponse({"status": 200})


@login_required(login_url='/accounts/login/')
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
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin=place_id:{places[0]}" \
          f"&destination=place_id:{places[-1]}" \
          f"{waypoints}" \
          f"&key={api_key}"
    response = requests.get(url)
    data = json.loads(response.text)
    return data


@login_required(login_url='/accounts/login/')
def get_travel_time(request) -> JsonResponse:
    """Get How long does it takes between places receiving POST method as a list of place id.

    POST params:
        places: list of places that will be calculated the direction ordered by items order in the list.
    """
    if request.method != 'POST':
        return JsonResponse({"status": "METHOD ERROR"})
    places = json.loads(request.POST['places'])
    if len(places) > 25:
        return JsonResponse({"status": "TOO MANY PLACES"})
    if len(places) <= 1:
        return JsonResponse({"status": "NOT ENOUGH PLACE"})
    data = get_direction(places)
    return JsonResponse(data)


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
    if user.first_name == "":
        plan_name = f"{user.username}'s Plan"
    else:
        plan_name = f"{user.first_name}'s Plan"
    plan = Plan.objects.create(name=plan_name, author=user)
    plan.save()
    return HttpResponseRedirect(reverse('planner:edit_plan', args=[plan.id], ))


@login_required
def delete_planner(request, planner_id):
    """Delete the planner and redirect to planner list page."""
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

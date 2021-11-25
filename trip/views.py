from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from allauth.account.decorators import verified_email_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
import os
from django.http.response import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
import shutil
import requests
from threpose.settings import BASE_DIR, MEDIA_ROOT
from src.caching.caching_gmap import APICaching
from decouple import config
from django.views.generic import ListView, UpdateView
from requests.api import post
from .models import TripPlan, Review, CategoryPlan, UploadImage
from .forms import TripPlanForm, TripPlanImageForm, ReviewForm
from django.contrib.auth.decorators import login_required
from django.core import serializers


api_caching = APICaching()


PLACE_IMG_PATH = os.path.join(
    BASE_DIR, 'media', 'places_image')


# View page
def index(request):
    """Render Index page."""
    api_key = config('FRONTEND_API_KEY')
    # Get top like trip blogs.
    top_trips = sorted(TripPlan.objects.filter(complete=True), key=lambda m: m.total_like, reverse=True)[:6]
    return render(request, "trip/index.html", {'api_key': api_key, "top_trips": top_trips})


@require_http_methods(["POST"])
def get_trip_queries(request):
    """Search for trip and return queries.

    POST params:
        keyword: keyword to search for trip plans.
    """
    if 'keyword' not in request.POST:
        return JsonResponse({"status": "BAD_REQUEST"})
    keyword = json.loads(request.POST['keyword'])
    # get query that has title starts with keyword.
    query_startswith = sorted(TripPlan.objects.filter(title__istartswith=keyword,
                                                      complete=True),
                              key=lambda m: m.total_like,
                              reverse=True)[:3]
    quantity_requested = 4 - len(query_startswith)  # define how much we need query left.
    # get query that contains keyword.
    query_contain = sorted(TripPlan.objects.filter(title__icontains=keyword,
                                                   complete=True),
                           key=lambda m: m.total_like,
                           reverse=True)[:quantity_requested]
    queries_combined = set(query_startswith + query_contain)  # list of query, type is list
    queries = [{"id": query.id, "name": query.title} for query in queries_combined]  # prepare for context
    return JsonResponse({"status": "OK", "results": queries})


class AllTrip(ListView):
    """Class for link html of show all trip page."""

    model = TripPlan
    template_name = 'trip/trip_plan.html'
    context_object_name = 'object'
    ordering = ['-id']

    def get_queryset(self):
        """Get variable to use in html.
        Return:
            content(dict): list of caliable can use in html.
        """
        content = {
            'post': TripPlan.objects.filter(complete=True),
            'category': CategoryPlan.objects.all()
        }
        return content


def trip_detail(request, pk):
    """Method for link html to trip detail and add review form.
    Args:
        pk(str): post id
    Return:
        Httpresponse(Http):redirect to trip detail page.
    """
    post = get_object_or_404(TripPlan, id=pk)
    commend = Review.objects.filter(post=post)
    page = request.GET.get('page', 1)

    paginator = Paginator(commend, 8)
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)

    context = {
        'post': post,
        'commend': commend,
        'comments': comments
    }
    return render(request, 'trip/trip_detail.html', context)


class CatsListView(ListView):
    """Class for link html of trip in each category."""

    template_name = 'trip/category.html'
    context_object_name = 'catlist'

    def get_queryset(self):
        """Get variable to use in html.
        Return:
            content(dict): list of caliable can use in html.
        """
        content = {
            'cat': self.kwargs['category'],
            'posts': TripPlan.objects.filter(category__name=self.kwargs['category']),
            'category': CategoryPlan.objects.all()
        }
        return content


@verified_email_required
def add_post(request):
    """Method for link html of add post page.
    Return:
        if post return to trip detail else return to add blog page.
    """
    if len(TripPlan.objects.filter(author=request.user, complete=False)) == 0:
        TripPlan.objects.create(author=request.user)
        image_form = TripPlanImageForm()
        post = get_object_or_404(TripPlan, author=request.user, complete=False)
        form = TripPlanForm(instance=post)
        image_form = TripPlanImageForm()
        return render(request, 'trip/add_blog.html', {'form': form, 'image_form': image_form})
    if request.method == 'POST':
        post = get_object_or_404(TripPlan, author=request.user, complete=False)
        form = TripPlanForm(request.POST, instance=post)
        if 'imgpic' in request.POST:
            image_form = TripPlanImageForm(request.POST, request.FILES)
            form = TripPlanForm(instance=post)
            post_form = form.save(commit=False)
            post_form.author = request.user
            post_form.save()
            if image_form.is_valid():
                image = request.FILES.getlist('image')
                list_img = []
                for img in image:
                    img_obj = UploadImage.objects.create(post=post, image=img)
                    img_obj.save()
                    list_img.append(img_obj)
                image_form = TripPlanImageForm()
                form = TripPlanForm(request.POST, instance=post)
                return render(request, 'trip/add_blog.html', {'form': form,
                                                              'image_form': image_form, 'img_obj': list_img})
            form = TripPlanForm(request.POST, instance=post)
            image_form = TripPlanImageForm()
            return render(request, 'trip/add_blog.html', {'form': form,
                                                          'image_form': image_form})
        elif 'blog' in request.POST:
            if form.is_valid():
                image_form = TripPlanImageForm(request.POST, request.FILES)
                post_form = form.save(commit=False)
                if post_form.body == '' or post_form.title is None or post_form.duration is None or post_form.price is None:
                    post_form.save()
                    return render(request, 'trip/add_blog.html', {'form': form,
                                                                  'image_form': image_form, 'message': 'Need fill all fields'})
                post_form.author = request.user
                post_form.complete = True
                post_form.save()
                return HttpResponseRedirect(reverse('trip:tripdetail', args=[post_form.pk]))
        elif 'save_blog' in request.POST:
            if form.is_valid():
                post_form = form.save(commit=False)
                post_form.author = request.user
                post_form.save()
                image_form = TripPlanImageForm()
                form = TripPlanForm(request.POST, instance=post)
                return render(request, 'trip/add_blog.html', {'form': form,
                                                              'image_form': image_form})
    post = get_object_or_404(TripPlan, author=request.user, complete=False)
    form = TripPlanForm(instance=post)
    image_form = TripPlanImageForm()
    return render(request, 'trip/add_blog.html', {'form': form, 'image_form': image_form})


class EditPost(UpdateView):
    """Class for link html of edit post."""

    model = TripPlan
    template_name = "trip/update_plan.html"
    # fields = ['title', 'duration', 'price', 'body']
    form_class = TripPlanForm
    context_object_name = 'post'


@login_required
def delete_post(request, pk):
    """Method for delete post and remove images in local.
    Args:
        pk(str): post id.
    Return:
        HttpResponse: Redirect to all trip page.
    """
    post = get_object_or_404(TripPlan, id=pk)
    if request.method == "POST":
        if request.user.id == post.author.id:
            image_path = os.path.join(MEDIA_ROOT, 'pic', str(pk))
            if os.path.exists(image_path):
                shutil.rmtree(image_path)
            post.delete()
            success_url = reverse_lazy('trip:tripplan')
            return redirect(success_url)
    context = {
        "post": post
    }
    return render(request, "trip/delete_plan.html", context)


@login_required
def like_comment_view(request):
    """Method that store user like in comment model"""
    if request.method == 'POST':
        post = get_object_or_404(Review, id=request.POST.get('comment_id'))
        if post.like.filter(id=request.user.id).exists():
            post.like.remove(request.user)
        else:
            post.like.add(request.user)
        return JsonResponse({'result': post.total_like, 'id': request.POST.get('comment_id')})


@login_required
def like_post(request):
    """Method for store user like of each trip.
    Args:
        pk(str): blog id of link located.
    Return:
        HttpResponse: Redirect to page that link blog located.
    """
    if request.method == 'POST':
        pk = request.POST.get('pk')
        post = get_object_or_404(TripPlan, id=pk)
        if post.like.filter(id=request.user.id).exists():
            post.like.remove(request.user)
        else:
            post.like.add(request.user)
        return JsonResponse({'post_result': post.total_like})


def place_info(request, place_id: str):
    """Render Place information page.
    Args:
        request: auto-generated by django.
        place_id: place identity defined by Google
    Returns:
        HttpRequest: Return 200 if place_id is correct, and return 404 if invalid.
    """
    backend_api_key = config('BACKEND_API_KEY')
    frontend_api_key = config('FRONTEND_API_KEY')
    if api_caching.get(f"{place_id[:50]}detailpage"):
        cache_data = json.loads(api_caching.get(
            f"{place_id[:50]}detailpage"))['cache']
    else:
        url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={backend_api_key}"
        response = requests.get(url)
        data = json.loads(response.content)
        if data['status'] != "OK":
            return HttpResponseNotFound(f"<h1>Response error with place_id: {place_id}</h1>")
        context = get_details_context(data, backend_api_key, frontend_api_key)
        cache_data = restruct_detail_context_data(context)
        api_caching.add(f"{place_id[:50]}detailpage", json.dumps(
            {'cache': cache_data}, indent=3).encode())

    context = resturct_to_place_detail(cache_data)
    context['blank_rating'] = range(round(context['blank_rating']))
    context['rating'] = range(round(context['rating']))
    context['api_key'] = frontend_api_key
    context = check_downloaded_image(context)
    return render(request, "trip/place_details.html", context)


# Helper function
def get_details_context(place_data: dict, backend_api_key: str, frontend_api_key: str) -> dict:
    """Get context for place details page.
    Args:
        place_data: The data received from Google Cloud Platform.
        backend_api_key:
        frontend_api_key: Exposed API key used to display images in website, restriction in GCP needed.
    Returns:
        context data needed for place details page.
    """
    context = {}
    if 'result' in place_data.keys():
        if 'name' in place_data['result'].keys():
            context['place_name'] = place_data['result']['name']
        else:
            context['place_name'] = "N/A"
        if 'place_id' in place_data['result'].keys():
            context['place_id'] = place_data['result']['place_id']
        else:
            context['place_id'] = "N/A"
        if 'types' in place_data['result'].keys():
            context['types'] = place_data['result']['types']
        else:
            context['types'] = []
        if 'formatted_phone_number' in place_data['result'].keys():
            context['phone'] = place_data['result']['formatted_phone_number']
        else:
            context['phone'] = "N/A"
        if 'website' in place_data['result'].keys():
            context['website'] = place_data['result']['website']
        else:
            context['website'] = "N/A"
        if 'rating' in place_data['result'].keys():
            context['rating'] = int(place_data['result']['rating'])
            context['blank_rating'] = 5 - int(place_data['result']['rating'])
        else:
            context['rating'] = 0
            context['blank_rating'] = 0
        if 'photos' in place_data['result'].keys():
            images = []
            current_photo = 0
            for data in place_data['result']['photos']:
                img_ref = data['photo_reference']
                images.append(img_ref)
                current_photo += 1
                if current_photo >= 4:
                    break
            context['images'] = images
        else:
            context['images'] = []
        reviews = []
        if 'reviews' in place_data['result'].keys():
            for i in place_data['result']['reviews']:
                if i['text'] != "":
                    reviews.append({
                        'author': i['author_name'],
                        'text': i['text']
                    })
        context['reviews'] = reviews
        lat, lng = None, None
        if 'geometry' in place_data['result'].keys():
            if 'location' in place_data['result']['geometry'].keys():
                if 'lat' in place_data['result']['geometry']['location'].keys():
                    lat = place_data['result']['geometry']['location']['lat']
                if 'lng' in place_data['result']['geometry']['location'].keys():
                    lng = place_data['result']['geometry']['location']['lng']
        if lat is not None and lng is not None:
            suggestions = []
            url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/" \
                f"json?location={lat}%2C{lng}&radius=2000&key={backend_api_key}"
            response = requests.get(url)
            place_data = json.loads(response.content)
            for place in place_data['results'][1:]:
                if place['name'] == context['place_name']:
                    continue
                if 'photos' not in place.keys():
                    continue
                img_ref = place['photos'][0]['photo_reference']
                suggestions.append({
                    'place_name': place['name'],
                    'photo_ref': img_ref,
                    'place_id': place['place_id']
                })
            context['suggestions'] = suggestions
    context['api_key'] = frontend_api_key
    return context


def check_downloaded_image(context):
    """Check that image from static/images/place_image that is ready for frontend to display or not"""
    if os.path.exists(PLACE_IMG_PATH):
        all_img_file = [f for f in os.listdir(
            PLACE_IMG_PATH) if os.path.isfile(os.path.join(PLACE_IMG_PATH, f))]
        place_id = context['place_id']
        context['downloaded'] = True
        if len(context['images']) > 1:
            for idx in range(len(context['images'])):
                if f'{place_id}_{idx}photo.jpeg' not in all_img_file:
                    context['downloaded'] = False
        else:
            if f'{place_id}photo.jpeg' not in all_img_file:
                context['downloaded'] = False
        if context['downloaded']:
            context['images'] = range(len(context['images']))
        for idx in range(len(context['suggestions'])):
            sug_id = context['suggestions'][idx]['place_id']
            if f'{sug_id}photo.jpeg' in all_img_file:
                context['suggestions'][idx]['downloaded'] = True
            else:
                context['suggestions'][idx]['downloaded'] = False
    return context


def restruct_detail_context_data(context):
    """Process data for frontend
    Args:
        places: A place nearby data from google map api.
    Returns:
        context: A place data that place-list page needed.
    Data struct:
    [   # main place data
        {
            # Essential key
            'place_name': <name>,
            'place_id': <place_id>,
            'photo_ref': [<photo_ref],
            'type': [],
            # other...
        }
        # sugguestion place data
        . . .
    ]
    """
    init_data = []
    main_data = {
        'place_name': context['place_name'],
        'place_id': context['place_id'],
        'photo_ref': [img for img in context['images']],
        'types': context['types'],
        'reviews': context['reviews'],
        'phone': context['phone'],
        'rating': context['rating'],
        'blank_rating': context['blank_rating']
    }
    if 'website' in context:
        main_data["website"] = context['website']
    init_data.append(main_data)
    init_data += context['suggestions']
    return init_data


def resturct_to_place_detail(context):
    """Convert cache data to place_detail data.
        {
            "place_name": <place_name>,
            "place_id": <place_id>,
            "types": [..<types>],
            "phone": <phone_number>,
            "website": <website>,
            "rating": <rating>,
            "blank_rating": <blank_rating>,
            "images": [],
            "reviews": [],
            "suggestions": []
        }
    """
    init_data = {
        "place_name": context[0]['place_name'],
        "place_id": context[0]['place_id'],
        "types": [context[0]['types']],
        "rating": context[0]['rating'],
        "blank_rating": context[0]['blank_rating'],
        "images": [img for img in context[0]['photo_ref']],
        "reviews": context[0]['reviews'],
        "suggestions": [place for place in context[1:]]
    }
    if 'website' in context[0]:
        init_data["website"] = context[0]['website']
    if 'phone' in context[0]:
        init_data["phone"] = context[0]['phone']
    return init_data


def new_line_html(text):
    out = ""
    for idx in range(len(text)):
        if text[idx] == '\n':
            out += '<br>'
        else:
            out += text[idx]
    return out


def post_comment(request):
    """Add comment to database and return html to render in front-end

    Returns:
        http: html of comment
    """
    if request.method == 'POST':
        pk = request.POST.get('pk')
        post = get_object_or_404(TripPlan, id=pk)
        comment = Review()
        comment.name = request.user
        comment.post = post
        comment.body = request.POST.get('comment')
        comment.body = new_line_html(comment.body)
        comment.save()
    return render(request, 'trip/single_comment.html', {'commend': comment})

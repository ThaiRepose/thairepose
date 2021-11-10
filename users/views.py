from django.shortcuts import render, get_object_or_404
from .models import Profile
# Create your views here.


def home(request):
    """Render home page."""
    return render(request, "users/temp_home.html")


def index(request):
    """Render index page."""
    return render(request, "users/index.html")


def profile(request):
    """Render Profile page.
    
    Return:
        HTTPResponse: link of profile and content.
    """
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, "users/profile.html", {'profile': profile})

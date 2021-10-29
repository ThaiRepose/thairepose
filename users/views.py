import django
from django.http import HttpResponse
from django.shortcuts import render
from allauth.account.views import LoginView, SignupView

# Create your views here.


def home(request):
    """Render home page."""
    return render(request, "users/temp_home.html")


def index(request):
    """Render index page."""
    return render(request, "users/index.html")

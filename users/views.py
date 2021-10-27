import django
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.urls import reverse

from .models import Profile, User
# Create your views here.


def home(request):
    """Render home page."""
    return render(request, "users/temp_home.html")


def index(request):
    """Render index page."""
    return render(request, "users/index.html")

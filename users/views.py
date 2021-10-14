import django
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text, force_str, DjangoUnicodeDecodeError
from django.conf import settings
from django.urls import reverse

from users.models import Customer, User
from .forms import CreateUserForm
from .utils import generate_token
# Create your views here.


def home(request):
    return render(request,"users/temp_home.html")

def index(request):
    return render(request, "users/index.html")

def register(request):
    form = CreateUserForm()
    
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name='customer')
            username = form.cleaned_data.get('username')
            user.groups.add(group)
            Customer.objects.create(
                user=user,
                username=username,
            )

    context = {'form':form}
    return render(request, "users/register.html", context)
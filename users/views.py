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

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.customer.is_email_verified:
                messages.info(request, 'Email is not verified, please check your email inbox')
            else:
                login(request, user)
                return redirect('temphome')
        else:
            messages.info(request, 'Username or Password is incorrect')

    context = {}
    return render(request, "users/login.html", context)
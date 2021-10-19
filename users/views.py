import django
from django.contrib.auth.models import Group
from django.http.response import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.http import HttpResponse, request
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

def send_action_email(user, request):
    current_site = get_current_site(request)
    email_subject = 'Activate your account'
    email_body = render_to_string('users/activate.html',{
        'user':user,
        'domain':current_site,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })

    email = EmailMessage(subject=email_subject, body=email_body, from_email=settings.EMAIL_FROM_USER,
                        to=[user.email]
                        )
    email.send()

def home(request):
    return render(request,"users/temp_home.html")

def index(request):
    return render(request, "users/index.html")

def activate_fail(request):
    return render(request, )

def register(request):
    form = CreateUserForm()
    
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            # group = Group.objects.get(name='customer')
            username = form.cleaned_data.get('username')
            # user.groups.add(group)
            Customer.objects.create(
                user=user,
                username=username,
            )
            send_action_email(user, request)

    context = {'form':form}
    return render(request, "users/register.html", context)

def loginPage(request):
    context = {
        'has_error':False
    }
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.customer.is_email_verified:
                messages.info(request, 'Email is not verified, please check your email inbox')
                context['has_error'] = True 
            else:
                login(request, user)
                return redirect('temphome')
        else:
            messages.info(request, 'Username or Password is incorrect')
            context['has_error'] = True 

    if context['has_error']:
        return render(request, "users/login.html", status=401)
        
    return render(request, "users/login.html")

def logoutUser(request):
    logout(request)
    return redirect('login')

def activate_user(request, uidb64, token):
    try:
        uid=force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception as e:
        user=None
        
    if user and generate_token.check_token(user, token):
        user.customer.is_email_verified = True
        user.customer.save()
        messages.info(request, 'Email verified')
        return redirect(reverse('login'))
    return render(request, 'users/activate-fail.html', {"user":user}, status=401)
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from PIL import Image
from .models import Profile
from .forms import UserUpdateForm, ProfileUpdateForm
from .utils import pic_profile_path, pic_profile_rename_path
import os


def home(request):
    """Render home page."""
    return render(request, "users/temp_home.html")


def index(request):
    """Render index page."""
    return render(request, "users/index.html")


@login_required
def profile(request):
    """Render Profile page.

    Args:
        request(HTTP): request from profiel page.

    Return:
        HTTPResponse: link of profile and content.
    """
    profile = get_object_or_404(Profile, user=request.user)
    user_form = UserUpdateForm(instance=request.user)
    profile_form = ProfileUpdateForm(instance=request.user.profile)
    context = {'profile': profile,
               'u_form': user_form,
               'p_form': profile_form,
               }
    return render(request, "users/profile.html", context)


def privacy_policy(request):
    return render(request, "policy/privacy_policy.html")


@login_required
def edit_profile(request):
    """Config fiel of user form and profile form.

    Args:
        request(hTTP): request from url of edit page.

    Return:
        HTTPResponse: link of profile and content.
    """
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            user_form.save()
            filename = profile_form.save(commit=False).profile_pic
            profile_form.save()
            im1 = Image.open(pic_profile_path(filename))
            im2 = Image.open(pic_profile_rename_path(request.user.pk))
            if list(im1.getdata()) != list(im2.getdata()):
                os.remove(pic_profile_rename_path(request.user.pk))
            os.rename(pic_profile_path(filename),
                      pic_profile_rename_path(request.user.pk))
            profile_form.save(commit=False).profile_pic = pic_profile_rename_path(request.user.pk)
            profile_form.save()
            messages.success(request, 'Your account has been updated!')
            return HttpResponseRedirect(reverse('profile'))
        elif user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your account has been updated!')
            return HttpResponseRedirect(reverse('profile'))
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    context = {'u_form': user_form,
               'p_form': profile_form,
               'profile': profile
               }
    return render(request, "users/edit_profile.html", context)

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from PIL import Image
from .models import Profile
from .forms import UserUpdateForm, ProfileUpdateForm
from .utils import get_upload_pic_path, pic_profile_path, pic_profile_rename_path, get_pic_profile_relate_path, rename_file
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


def term_of_service(request):
    return render(request, "policy/term_of_service.html")


@login_required
def edit_profile(request):
    """Config fiel of user form and profile form.

    Args:
        request(hTTP): request from url of edit page.

    Return:
        HTTPResponse: link of profile and content.
    """
    n = Profile.objects.get(user__id=request.user.id)
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            user_form.save()
            if os.path.isfile(pic_profile_rename_path(request.user.pk)):
                os.remove(pic_profile_rename_path(request.user.pk))
            else:
                os.remove(get_upload_pic_path(n.profile_pic.name))
            profile_form.save()
            filename = profile_form.save(commit=False).profile_pic
            name = filename.name.split('/')[-1]
            os.rename(pic_profile_path(name),
                      rename_file(request.user.pk, name))
            profile_form.save(commit=False).profile_pic = get_pic_profile_relate_path(
                request.user.pk, name)
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

from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile
from .forms import UserUpdateForm, ProfileUpdateForm


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


@login_required
def edit_profile(request):
    """Config fiel of user form and profile form.

    Args:
        request(hTTP): request from url of edit page.

    Return:
        HTTPResponse: link of profile and content.
    """
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    context = {'u_form': user_form,
               'p_form': profile_form
               }
    return render(request, "users/edit_profile.html", context)

from django.conf import settings

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect, resolve_url
from django.http import HttpResponseRedirect
from django.urls import reverse
from allauth.account.models import EmailAddress

from .models import Profile
from .utils import upload_profile_pic


class ProfileAccountAdapter(DefaultAccountAdapter):
    """Extended django-allauth class."""

    def save_user(self, request, user, form, commit=True):
        """Save_user() function that extended from django-allauth.

        This function add user to profile model that provided by Signup form.

        Args:
            user (User): user model
            form (SignupForm): form for signup
            commit (bool): If True, save user. Defaults to True.

        Returns:
            User: user model
        """
        user = super(ProfileAccountAdapter, self).save_user(
            request, user, form, commit
        )
        Profile.objects.create(
            user=user
        )
        upload_profile_pic(user, None, str(user.id) + "_profile_picture.jpg")
        if 'user_email' in request.session:
            del request.session['user_email']
        request.session['user_email'] = user.email
        return user

    def get_signup_redirect_url(self, request):
        """Redirect to home page if user already verified and redirect to redirect_url if user not verifed.

        Returns:
            str: url of page that want to redirect
        """
        user = EmailAddress.objects.filter(
            user=request.user)
        if user[0].verified:
            return resolve_url('/')
        return resolve_url(settings.ACCOUNT_SIGNUP_REDIRECT_URL)


class ProfileSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Extended django-allauth class."""

    def save_user(self, request, sociallogin, form=None):
        """Save_user() function that extened from django-allauth function.

        This function add user and user profile picture from sociallogin to profile model.

        Args:
            sociallogin (Social): Object of each social login. Depend on type of socail
            form (SignupForm): form for signup.

        Returns:
            User: user model
        """
        user = super(ProfileSocialAccountAdapter, self).save_user(
            request, sociallogin, form
        )
        Profile.objects.create(
            user=user,
        )
        try:
            picture_url = sociallogin.account.get_avatar_url()
            upload_profile_pic(user, picture_url, str(
                user.id) + "_profile_picture.jpg")
        except (KeyError, AttributeError):
            pass

        if 'user_email' in request.session:
            del request.session['user_email']
        request.session['user_email'] = 'SocialLogin'

        return user

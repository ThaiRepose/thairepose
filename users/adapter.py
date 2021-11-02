from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpResponseRedirect
from django.urls import reverse

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


    def respond_email_verification_sent(self, request, user):
        """Show email_verification_sent page with assign user_email variable to request.session.

        Args:
            user (Usser): user model

        Returns:
            Httpresponse: redirect to account_email_verification_sent
        """
        if 'user_email' in request.session:
            del request.session['user_email']
        request.session['user_email'] = user.email
        return HttpResponseRedirect(reverse("account_email_verification_sent"))


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

        return user

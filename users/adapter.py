from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from django.conf import settings
from .models import Profile
from .utils import upload_profile_pic

class ProfileAccountAdapter(DefaultAccountAdapter):
    
    def save_user(self, request, user, form, commit=True):
        user = super(ProfileAccountAdapter, self).save_user(
            request, user, form, commit
        )
        Profile.objects.create(
            user = user
        )
        return user


class ProfileSocialAccountAdapter(DefaultSocialAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        user = super(ProfileSocialAccountAdapter, self).save_user(
            request, sociallogin, form
        )
        Profile.objects.create(
            user = user,
        )
        try:
            picture_url = sociallogin.account.get_avatar_url()
            upload_profile_pic(user, picture_url, settings.PROFILE_PIC_LOCATION, str(user.id)+"_profile_picture.jpg")
        except (KeyError, AttributeError):
            pass
        
        return user

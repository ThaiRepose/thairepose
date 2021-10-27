from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .models import Profile

class ProfileAccountAdapter(DefaultAccountAdapter):
    
    def save_user(self, request, user, form, commit=True):
        user = super(ProfileAccountAdapter, self).save_user(
            request, user, form, commit
        )
        Profile.objects.create(
            user = user
        )
        print("save no Oauth")
        return user


# class ProfileSocialAccountAdapter(DefaultSocialAccountAdapter):
#     def save_user(self, request, sociallogin, form=None):
#         user = super(ProfileSocialAccountAdapter, self).save_user(
#             request, sociallogin, form
#         )
#         picture_url = sociallogin.account.get_avatar_url()
#         print(picture_url)
#         Profile.objects.create(
#             user = user,
#         )
#         print("save social user")

#         return user

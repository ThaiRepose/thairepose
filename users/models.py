from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Profile(models.Model):
    """Extended user model class that use for user profile.

    Attributes:
        birthday(str): user birthday
        profile_pic(image): user profile image
    """
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    birthday = models.DateField(null=True, auto_now=False, auto_now_add=False)
    profile_pic = models.ImageField(upload_to=None ,null=True, blank=True)

    def __str__(self):
        """Return username.

        Returns:
            str: username of model
        """
        return str(self.user)

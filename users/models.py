from django.db import models
from django.contrib.auth.models import User
from .utils import pic_profile_relative_path
from PIL import Image


class Profile(models.Model):
    """Extended user model class that use for user profile.

    Attributes:
        user(User): user model
        birthday(str): user birthday
        profile_pic(image): user profile image
    """

    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    birthday = models.DateField(null=True, auto_now=False, auto_now_add=False)
    profile_pic = models.ImageField(
        upload_to=pic_profile_relative_path(), null=True, blank=True)

    def __str__(self):
        """Return username.

        Returns:
            str: username of model
        """
        return str(self.user.username)

    def save(self):
        super().save()
        img = Image.open(self.profile_pic)
        if img.height > 200 and img.width > 300:
            outpit_size = (200, 300)
            img.thumbnail(outpit_size)
            img.save(self.profile_pic.path)

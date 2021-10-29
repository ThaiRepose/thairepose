from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User
from PIL import Image
import tempfile
from django.test import TestCase
from django.test import override_settings
from django.conf import settings

from .models import Profile
from .utils import upload_profile_pic

# Create your tests here.
class TestProfileModel(TestCase):

    def test_profile(self):
        user = User.objects.create(
            username = 'harry',
            email = 'harry@email.com',
            password = 'johnpotter223'
        )
        Profile.objects.create(
            user = user
        )
        self.assertEqual(str(user.profile), user.username)
        

class TestUploadPircute(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            username = 'harry',
            email = 'harry@email.com',
            password = 'johnpotter223'
        )
        Profile.objects.create(
            user = self.user
        )
    
    # def test_upload_profile_pic_success(self):
    #     upload_profile_pic(self.user, None, settings.PROFILE_PIC_LOCATION, 'blank-profile-picture.png', testing=True)

    # def test_wrong_url(self):
    #     upload_profile_pic(self.user, None, settings.PROFILE_PIC_LOCATION, 'blank-profile-picture.png', testing=False)


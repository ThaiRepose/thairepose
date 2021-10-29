from .utils import upload_profile_pic
from django.contrib.auth.models import User
from django.conf import settings
from django.test import TestCase
from .models import Profile

import os

# Create your tests here.
class TestProfileModel(TestCase):

    def test_profile(self):
        """Test profile model"""
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
        """Set up profile model for test upload picture"""
        self.user = User.objects.create(
            username = 'harry',
            email = 'harry@email.com',
            password = 'johnpotter223'
        )
        Profile.objects.create(
            user = self.user
        )


    def tearDown(self):
        """For remove file that create while testing"""
        os.remove(settings.PROFILE_PIC_LOCATION + 'test.png')
    

    def test_upload_profile_pic_success(self):
        """Test upload picture to profile model"""
        upload_profile_pic(self.user, None, 'test.png', True)
        self.assertEqual(settings.PROFILE_PIC_LOCATION + 'test.png', self.user.profile.profile_pic)


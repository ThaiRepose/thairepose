from .utils import upload_profile_pic
from django.contrib.auth.models import User
from django.conf import settings
from django.test import TestCase
from .models import Profile
from django.db import models

import os

# Create your tests here.


class TestProfileModel(TestCase):
    """Test profile model."""

    def test_profile(self):
        """Test profile model."""
        user = User.objects.create(
            username='harry',
            email='harry@email.com',
            password='johnpotter223'
        )
        Profile.objects.create(
            user=user
        )
        self.assertEqual(str(user.profile), user.username)


class TestUploadPircute(TestCase):
    """Test upload picture function."""

    def setUp(self) -> None:
        """Set up profile model for test upload picture."""
        self.user = User.objects.create(
            username='harry',
            email='harry@email.com',
            password='johnpotter223'
        )
        Profile.objects.create(
            user=self.user
        )

    def test_upload_profile_pic_success(self):
        """Test upload picture to profile model."""
        upload_profile_pic(self.user, None, 'test.png', True)
        self.assertNotEqual(self.user.profile.profile_pic, None)

    def tearDown(self):
        """For remove file that create while testing. if file created"""
        path = os.path.join(settings.PROFILE_PIC_LOCATION, 'test.png')
        if os.path.isfile(path):
            os.remove(path)
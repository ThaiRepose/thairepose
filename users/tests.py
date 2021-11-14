from .utils import upload_profile_pic
from django.contrib.auth.models import User
from django.conf import settings
from django.test import TestCase, RequestFactory
from .models import Profile
from .adapter import ProfileAccountAdapter

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
        """For remove file that create while testing. if file created."""
        path = os.path.join(settings.PROFILE_PIC_LOCATION, 'test.png')
        if os.path.isfile(path):
            os.remove(path)


class TestEmailVerificationPage(TestCase):
    """Test response_email_verification."""

    def setUp(self) -> None:
        """Set up profile and request."""
        self.rf = RequestFactory
        self.rf.session = {}
        self.user = User.objects.create(username='test',
                                        password='123',
                                        email='test@email.com'
                                        )

    def test_template(self):
        """Test template and response code of response email verification page."""
        response = ProfileAccountAdapter.respond_email_verification_sent(ProfileAccountAdapter, self.rf, self.user)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('verification_sent.html')

    def test_email_already_in_session(self):
        """Test template and response code of response email verification page with user_email aready in session."""
        self.rf.session = {'user_email': 'test@email.com'}
        response = ProfileAccountAdapter.respond_email_verification_sent(ProfileAccountAdapter, self.rf, self.user)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('verification_sent.html')

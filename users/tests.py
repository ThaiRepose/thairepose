from django.http import request, response
from django.test.testcases import _AssertTemplateNotUsedContext
from django.urls import reverse
from django.contrib.auth import get_user_model, tokens
from django.test import TestCase, Client, RequestFactory
from django.core import mail
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

import users
from .views import activate_user
from .models import Customer
from .utils import generate_token

# Create your tests here.
class TestEmailSend(TestCase):
    """Test send email."""

    def email_backend_setup(self, settings):
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

    def user_setup(self):
        self.user = Customer.objects.create_user('Tester', 'test@example.com', 'Password123')

    def test_send(self):
        mail.send_mail('subject', 'body.', 'from@example.com', ['to@example.com'])
        assert len(mail.outbox) == 1

class TestRegister(TestCase):
    """Test user register"""

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.user1 = {
            'username': 'TestUser1',
            'email': 'testuser@email.com',
            'password1': 'Password1234@',
            'password2': 'Password1234@'
        }
    
    def email_backend_setup(self, settings):
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

    def test_template(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_register_email_send(self):
        response = self.client.post(self.register_url, data=self.user1)
        self.assertEqual(response.status_code, 200)
        assert len(mail.outbox) == 1


# class TestActivateUser(TestCase):
    
#     def setUp(self):
#         self.client = Client()
#         self.user1 = {
#             'username': 'TestUser1',
#             'email': 'testuser@email.com',
#             'password1': 'Password1234@',
#             'password2': 'Password1234@'
#         }
#         self.register_url = reverse('register')
    
#     def test_activate_success(self):
#         self.client.post(self.register_url, self.user1)
#         user = User.objects.filter(email=self.user1['email']).first()
#         self.token = generate_token.make_token(user)
#         self.uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
#         response = self.client.post('activate-user/<uidb64>/<token>', {'token':self.token,'uidb64':self.uidb64})
#         print(response)
#         self.assertEqual(200, response.status_code)
        

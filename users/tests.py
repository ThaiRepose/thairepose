from django.http import request, response
from django.test.testcases import _AssertTemplateNotUsedContext
from django.urls import reverse
from django.test import TestCase, Client
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

    def test_template(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_register_email_send(self):
        response = self.client.post(self.register_url, data=self.user1)
        self.assertEqual(response.status_code, 200)
        assert len(mail.outbox) == 1

class TestLogin(TestCase):
    """Test user login"""

    def setUp(self) -> None:
        self.client = Client()
        self.login_url = reverse('login')
        self.register_url = reverse('register')
        self.user1 = {
            'username': 'TestUser1',
            'email': 'testuser@email.com',
            'password1': 'Password1234@',
            'password2': 'Password1234@'
        }
        self.client.post(self.register_url, self.user1)

    def test_template(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_not_verified_login(self):
        user = User.objects.filter(email=self.user1['email']).first()
        user.customer.is_email_verified = False
        user.customer.save()
        response = self.client.post(self.login_url, {'username': self.user1['username'], 'password': self.user1['password1']})
        self.assertEqual(response.status_code, 401)

    def test_can_login(self):
        user = User.objects.filter(email=self.user1['email']).first()
        user.customer.is_email_verified = True
        user.customer.save()
        response = self.client.post(self.login_url, {'username': self.user1['username'], 'password': self.user1['password1']})
        self.assertEqual(response.status_code, 302)

    def test_wrong_password(self):
        user = User.objects.filter(email=self.user1['email']).first()
        user.customer.is_email_verified = True
        user.customer.save()
        response = self.client.post(self.login_url, {'username': self.user1['username'], 'password': 'Aaaaa123'})
        self.assertEqual(response.status_code, 401)

class TestLogout(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.register_url = reverse('register')
        self.logout_url = reverse('logout')
        self.user1 = {
            'username': 'TestUser1',
            'email': 'testuser@email.com',
            'password1': 'Password1234@',
            'password2': 'Password1234@'
        }
        self.client.post(self.register_url, self.user1)
        user = User.objects.filter(email=self.user1['email']).first()
        user.customer.is_email_verified = True
        user.customer.save()
    
    def test_logout(self):
        self.client.login(username=self.user1['username'], password=self.user1['password1'])
        response = self.client.get(reverse('temphome'))
        self.assertEqual(response.status_code, 200)
        self.client.post(self.logout_url)
        self.assertTemplateUsed('login.html')

class TestActivateUser(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user1 = {
            'username': 'TestUser1',
            'email': 'testuser@email.com',
            'password1': 'Password1234@',
            'password2': 'Password1234@'
        }
        self.user2 = {
            'username': 'TestUser2',
            'email': 'testuser2@email.com',
            'password1': 'Password1234@',
            'password2': 'Password1234@'
        }
        self.register_url = reverse('register')
        
    
    def test_activate_success(self):
        self.client.post(self.register_url, self.user1)
        user = User.objects.filter(email=self.user1['email']).first()

        self.token = generate_token.make_token(user)
        self.uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        url = reverse('activate', args=[self.uidb64, self.token])
        response = self.client.post(url)

        self.assertEqual(302, response.status_code)
        self.assertTemplateNotUsed('users/activation-fail.html')

    def test_activate_user_fail(self):
        self.client.post(self.register_url, self.user1)

        user = User.objects.filter(email=self.user1['email']).first()

        self.token = generate_token.make_token(user)
        self.uidb64 = None

        url = reverse('activate', args=[self.uidb64, self.token])
        response = self.client.post(url)

        self.assertEqual(401, response.status_code)
        self.assertTemplateUsed('users/activation-fail.html')

    def test_activate_token_fail(self):
        self.client.post(self.register_url, self.user1)
        self.client.post(self.register_url, self.user2)

        user = User.objects.filter(email=self.user1['email']).first()
        user2 = User.objects.filter(email=self.user2['email']).first()

        self.token = generate_token.make_token(user2)
        self.uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        url = reverse('activate', args=[self.uidb64, self.token])
        response = self.client.post(url)

        self.assertEqual(401, response.status_code)
        self.assertTemplateUsed('users/activation-fail.html')

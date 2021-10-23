"""This file contain unittest."""

from django.http import request
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


class TestModel(TestCase):
    """Test model."""

    def setUp(self):
        """Set up for test model."""
        self.client = Client()

    def test_customer_model(self):
        """Test user string of user model."""
        self.register_url = reverse('register')
        self.user1 = {
            'username': 'TestUser1',
            'email': 'testuser@email.com',
            'password1': 'Password1234@',
            'password2': 'Password1234@'
        }
        self.client.post(self.register_url, self.user1)
        user = User.objects.filter(email=self.user1['email']).first()
        self.assertEqual(self.user1['username'], str(Customer.objects.filter(user=user).first()))


class TestRegister(TestCase):
    """Test user register."""

    def setUp(self):
        """Set up for register."""
        self.client = Client()
        self.register_url = reverse('register')
        self.user1 = {
            'username': 'TestUser1',
            'email': 'testuser@email.com',
            'password1': 'Password1234@',
            'password2': 'Password1234@'
        }
        self.user2 = {
            'username': 'TestUser2',
            'email': 'testuser@email.com',
            'password1': 'Password1234@',
            'password2': 'Password1234@'
        }
        self.user3 = {
            'username': 'TestUser1',
            'email': 'testuser2@email.com',
            'password1': 'Password1234@',
            'password2': 'Password1234@'
        }
        self.user4 = {
            'username': 'TestUser4',
            'email': 'testuser@email.com',
            'password1': 'Password1234',
            'password2': 'Password1234@'
        }

    def test_template(self):
        """Test register template."""
        response = self.client.get(self.register_url)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_register_email_send(self):
        """Test email send after register."""
        response = self.client.post(self.register_url, data=self.user1)
        self.assertEqual(response.status_code, 200)
        assert len(mail.outbox) == 1

    def test_email_exist(self):
        """Test user email is alreafy exist"""
        self.client.post(self.register_url, data=self.user1)
        response = self.client.post(self.register_url, data=self.user2)
        self.assertEqual(response.status_code, 403)
        

    def test_username_exist(self):
        """Test username is already exist"""
        self.client.post(self.register_url, data=self.user1)
        response = self.client.post(self.register_url, data=self.user3)
        self.assertEqual(response.status_code, 403)

    def test_password_not_match(self):
        """Test password1 and password2 is already exist"""
        response = self.client.post(self.register_url, data=self.user4)
        self.assertEqual(response.status_code, 403)


class TestLogin(TestCase):
    """Test user login."""

    def setUp(self):
        """Set up for login."""
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
        """Test login template."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_not_verified_login(self):
        """Test login with user not verified."""
        user = User.objects.filter(email=self.user1['email']).first()
        user.customer.is_email_verified = False
        user.customer.save()
        response = self.client.post(self.login_url, {'username': self.user1['username'],
                                                     'password': self.user1['password1']})
        self.assertEqual(response.status_code, 401)

    def test_can_login(self):
        """Test login with user already verified."""
        user = User.objects.filter(email=self.user1['email']).first()
        user.customer.is_email_verified = True
        user.customer.save()
        response = self.client.post(self.login_url, {'username': self.user1['username'],
                                                     'password': self.user1['password1']})
        self.assertEqual(response.status_code, 302)

    def test_wrong_password(self):
        """Test login with wrong password."""
        user = User.objects.filter(email=self.user1['email']).first()
        user.customer.is_email_verified = True
        user.customer.save()
        response = self.client.post(self.login_url, {'username': self.user1['username'], 'password': 'Aaaaa123'})
        self.assertEqual(response.status_code, 401)

    def test_wrong_user(self):
        """Test login with wrong user."""
        user = User.objects.filter(email=self.user1['email']).first()
        user.customer.is_email_verified = True
        user.customer.save()
        response = self.client.post(self.login_url, {'username': 'Aaaaa', 'password': self.user1['password1']})
        self.assertEqual(response.status_code, 401)


class TestLogout(TestCase):
    """Test user logout."""

    def setUp(self):
        """Set up for logout."""
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
        """Test user logout."""
        self.client.login(username=self.user1['username'], password=self.user1['password1'])
        response = self.client.get(reverse('temphome'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.logout_url)
        self.assertTemplateUsed('login.html')
        self.assertEqual(response.status_code, 302)


class TestActivateUser(TestCase):
    """Test user activation."""

    def setUp(self):
        """Set up for activate user."""
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
        """Test user activation success."""
        self.client.post(self.register_url, self.user1)
        user = User.objects.filter(email=self.user1['email']).first()

        self.token = generate_token.make_token(user)
        self.uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        url = reverse('activate', args=[self.uidb64, self.token])
        response = self.client.post(url)

        self.assertEqual(302, response.status_code)
        self.assertTemplateNotUsed('users/activation-fail.html')

    def test_activate_user_fail(self):
        """Test user activation with user fail."""
        self.client.post(self.register_url, self.user1)

        user = User.objects.filter(email=self.user1['email']).first()

        self.token = generate_token.make_token(user)
        self.uidb64 = None

        url = reverse('activate', args=[self.uidb64, self.token])
        response = self.client.post(url)

        self.assertEqual(401, response.status_code)
        self.assertTemplateUsed('users/activation-fail.html')

    def test_activate_token_fail(self):
        """Test user activation with token fail."""
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

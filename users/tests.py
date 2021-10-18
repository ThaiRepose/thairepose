from django.http import response
from django.test import TestCase, Client, client
from django.core import mail
from .views import send_action_email
from .models import Customer

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
        self.register_url = reversed('register')
    
    def email_backend_setup(self, settings):
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


    def test_template(self):
        pass
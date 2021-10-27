from django.urls import reverse
from django.test import TestCase, Client
from django.core import mail
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from .utils import generate_token

# Create your tests here.

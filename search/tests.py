from django.test import TestCase
from mock import Mock, patch
from .api import GoogleAPI
# Create your tests here.

class TestGoogleAPI(TestCase):
    def setUp(self):
        gmap_api = GoogleAPI()


    def test_search_nearby(self):
        lat = 1.23435
        lng = 2.3213
        self.gmap_api.search_nearby(lat,lng, type)
from django.test import TestCase
from django.urls import reverse
from .views import get_details_context
from dotenv import load_dotenv
import os


# Create your tests here.
class PlaceDetailsViewTest(TestCase):
    """Test for place details page."""

    def setUp(self):
        """Initialize API key from env."""
        load_dotenv()
        self.frontend_api_key = os.getenv('FRONTEND_API_KEY')

    def test_view_one_place(self):
        """Test viewing Kasetsart University (place_id = ChIJVysBBt6c4jARcDELPbMAAQ8)
        because there are completely informations."""
        response = self.client.get(reverse('trip:place', args=['ChIJVysBBt6c4jARcDELPbMAAQ8']))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['images'], list)
        self.assertIsInstance(response.context['suggestions'], list)
        self.assertIsInstance(response.context['reviews'], list)
        self.assertIsInstance(response.context['rating'], range)
        self.assertIsInstance(response.context['blank_rating'], range)
        self.assertEqual(response.context['name'], "Kasetsart University")
        self.assertEqual(response.context['phone'], "02 942 8200")
        self.assertEqual(response.context['website'], "http://www.ku.ac.th/")

    def test_invalid_place_id(self):
        """Test viewing place details page with invalid place_id."""
        response = self.client.get(reverse('trip:place', args=['123']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual("Place not found.", response.context['err_msg'])

    def test_get_details_function(self):
        """Test for get_details_context() function."""
        mock_data = {
            "result": {
                'name': "Tawan Boonma",
                'formatted_phone_number': "191",
                'website': "tawanb.dev",
                'rating': 4.4,
                'photos': [{'photo_reference': "1234"}]
            }
        }
        expected_photo_url = f"https://maps.googleapis.com/maps/api/place/photo?" \
                             f"maxwidth=600&photo_reference=1234&key={self.frontend_api_key}"
        context = get_details_context(mock_data, self.frontend_api_key)
        self.assertEqual("Tawan Boonma", context['name'])
        self.assertEqual("191", context['phone'])
        self.assertEqual("tawanb.dev", context['website'])
        self.assertEqual(range(4), context['rating'])
        self.assertEqual(range(1), context['blank_rating'])
        self.assertIn(expected_photo_url, context['images'])
        self.assertNotIn('reviews', context.keys())
        self.assertNotIn('suggestions', context.keys())


class IndexViewTest(TestCase):
    """Test for index page."""

    def test_response(self):
        """Test response for directing index page."""
        response = self.client.get(reverse('trip:index'))
        self.assertEqual(response.status_code, 200)

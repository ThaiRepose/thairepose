from django.test import TestCase, RequestFactory
from django.urls import reverse
from dotenv import load_dotenv
import os
import unittest
from .views import get_details_context
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Review, TripPlan, CategoryPlan
from django.db import models


class PlaceDetailsViewTest(TestCase):
    """Test for place details page."""

    def setUp(self):
        """Initialize API key from env."""
        load_dotenv()
        self.frontend_api_key = os.getenv('API_KEY')

    def test_invalid_place_id(self):
        """Test viewing place details page with invalid place_id."""
        response = self.client.get(reverse('trip:place-detail', args=['123']))
        self.assertEqual(response.status_code, 404)

    def test_get_details_function(self):
        """Test for get_details_context() function."""
        mock_data = {
            "result": {
                'name': "Tawan Boonma",
                'formatted_phone_number': "191",
                'website': "tawanb.dev",
                'rating': 4.4,
                'photos': [{'photo_reference': "1234"}],
                'reviews': [{'author_name': "Tawan", "text": "Good"},
                            {'author_name': "Unknown", "text": ""}],
                'geometry': {'location': {'lat': 10, 'lng': 10}}
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
        self.assertEqual(1, len(context['reviews']))
        self.assertIsInstance(context['suggestions'], list)

    def test_empty_get_details_function(self):
        """Test for get_details_context() function with empty place_data."""
        context = get_details_context({}, self.frontend_api_key)
        self.assertEqual({'api_key': None}, context)

    @unittest.skip("Skip due to not provided API key.")
    def test_view_one_place(self):
        """Test viewing Kasetsart University (place_id = ChIJVysBBt6c4jARcDELPbMAAQ8)
        because there are completely informations."""
        response = self.client.get(
            reverse('trip:place-detail', args=['ChIJVysBBt6c4jARcDELPbMAAQ8']))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['images'], list)
        self.assertIsInstance(response.context['suggestions'], list)
        self.assertIsInstance(response.context['reviews'], list)
        self.assertIsInstance(response.context['rating'], range)
        self.assertIsInstance(response.context['blank_rating'], range)
        self.assertEqual(response.context['name'], "Kasetsart University")
        self.assertEqual(response.context['phone'], "02 942 8200")
        self.assertEqual(response.context['website'], "http://www.ku.ac.th/")


class IndexViewTest(TestCase):
    """Test for index page."""

    def test_response(self):
        """Test response for directing index page."""
        response = self.client.get(reverse('trip:index'))
        self.assertEqual(response.status_code, 200)


class ReviewModelTests(TestCase):
    """Test Review Model"""

    def setUp(self):
        """Set up trip plan for create review"""
        self.request = RequestFactory()
        self.cat = CategoryPlan.objects.create(name='category1')
        self.user = User.objects.create(username='tester', password='tester')
        self.trip = TripPlan.objects.create(
            title='test', body='create_trip', author=self.user, duration=1, price=1, category=self.cat)

    def test_create_review(self):
        """Test create new review."""
        Review.objects.create(post=self.trip, name=self.user, body='review')
        self.assertEqual(Review.objects.count(), 1)
        Review.objects.create(post=self.trip, name=self.user, body='review')
        self.assertEqual(Review.objects.count(), 2)
        Review.objects.filter(id='1').delete()
        self.assertEqual(Review.objects.count(), 1)

    def test_like_one_user(self):
        """Test like comment."""
        Review.objects.create(post=self.trip, name=self.user, body='review')
        post = get_object_or_404(Review, id='1')
        post.like.add(self.user)
        self.assertEqual(post.total_like, 1)

    def test_like_more_than_one_user(self):
        """Test When like with different user."""
        Review.objects.create(post=self.trip, name=self.user, body='review')
        post = get_object_or_404(Review, id='1')
        post.like.add(self.user)
        user2 = User.objects.create(username='tester2', password='tester2')
        post.like.add(user2)
        self.assertEqual(post.total_like, 2)

    def test_dont_count_like_by_same_user(self):
        """Test don't count when same user like."""
        Review.objects.create(post=self.trip, name=self.user, body='review')
        post = get_object_or_404(Review, id='1')
        post.like.add(self.user)
        post.like.add(self.user)
        self.assertEqual(post.total_like, 1)

    def test_delete_post_review_will_delete(self):
        """Test if post is deleted the all review in deleted post will delete."""
        Review.objects.create(post=self.trip, name=self.user, body='review')
        TripPlan.objects.filter(id='1').delete()
        self.assertEqual(Review.objects.all().count(), 0)

    def tearDown(self):
        """Remove all user and all trip plan"""
        User.objects.all().delete()
        TripPlan.objects.all().delete()


class TripModelTests(TestCase):
    """Test for TripPlan functions."""

    def setUp(self):
        """Set up trip, user and category."""
        self.cat = CategoryPlan.objects.create(name='category1')
        self.user = User.objects.create(username='tester', password='tester')
        self.trip = TripPlan.objects.create(
            title='test', body='create_trip', author=self.user, duration=1, price=1, category=self.cat)
        return super().setUp()

    def test_create_post_in_category(self):
        """Test create post that have category."""
        self.assertEqual(TripPlan.objects.filter(
            category=self.cat)[0].category.name, 'category1')

    def test_have_more_than_one_post_in_same_category(self):
        """Test have more than one post that have same category."""
        TripPlan.objects.create(
            title='test2', body='create_trip2', author=self.user, duration=1, price=1, category=self.cat)
        self.assertEqual(TripPlan.objects.filter(category=self.cat).count(), 2)

    def test_like_post(self):
        """Test like post."""
        post = get_object_or_404(TripPlan, id='1')
        post.like.add(self.user)
        self.assertEqual(TripPlan.objects.filter(id='1')[0].total_like(), 1)

    def test_like_more_than_one_user(self):
        """Test have more than one user like same post."""
        self.user2 = self.user = User.objects.create(
            username='tester2', password='tester2')
        post = get_object_or_404(TripPlan, id='1')
        post.like.add(self.user)
        post.like.add(self.user2)
        self.assertEqual(TripPlan.objects.filter(id='1')[0].total_like(), 1)

    def test_dont_count_like_by_same_user(self):
        """Test post like not count user like if same user."""
        post = get_object_or_404(TripPlan, id='1')
        post.like.add(self.user)
        post.like.add(self.user)
        self.assertEqual(TripPlan.objects.filter(id='1')[0].total_like(), 1)

    def test_cant_delete_category_when_have_post_in_category(self):
        with self.assertRaises(models.ProtectedError):
            CategoryPlan.objects.filter(name='category1').delete()

    def tearDown(self):
        """Reset all user, all category and all tripplan"""
        User.objects.all().delete()
        TripPlan.objects.all().delete()
        CategoryPlan.objects.all().delete()
        return super().tearDown()

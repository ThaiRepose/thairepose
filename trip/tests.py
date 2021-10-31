from django.test import TestCase, RequestFactory
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Review, TripPlan


class ReviewModelTests(TestCase):
    """Test Review Model"""

    def setUp(self):
        """Set up trip plan for create review"""
        self.request = RequestFactory()
        self.user = User.objects.create(username='tester', password='tester')
        self.trip = TripPlan.objects.create(
            title='test', body='create_trip', author=self.user)

    def test_create_review(self):
        """Test create new review."""
        Review.objects.create(post=self.trip, name='reviewer', body='review')
        self.assertEqual(Review.objects.count(), 1)
        Review.objects.create(post=self.trip, name='reviewer', body='review')
        self.assertEqual(Review.objects.count(), 2)
        Review.objects.filter(id='1').delete()
        self.assertEqual(Review.objects.count(), 1)

    def test_like_one_user(self):
        """Test like comment."""
        Review.objects.create(post=self.trip, name='reviewer', body='review')
        post = get_object_or_404(Review, id='1')
        post.like.add(self.user)
        self.assertEqual(post.total_like, 1)

    def test_like_more_than_one_user(self):
        """Test When like with different user."""
        Review.objects.create(post=self.trip, name='reviewer', body='review')
        post = get_object_or_404(Review, id='1')
        post.like.add(self.user)
        user2 = User.objects.create(username='tester2', password='tester2')
        post.like.add(user2)
        self.assertEqual(post.total_like, 2)

    def tearDown(self):
        """Remove all user and all trip plan"""
        User.objects.all().delete()
        TripPlan.objects.all().delete()

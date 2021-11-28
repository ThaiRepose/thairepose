from django.http import response
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.utils import timezone
from decouple import config
from allauth.account.models import EmailAddress
import os
import unittest
from threpose.settings import BASE_DIR
from .views import delete_post, get_details_context, trip_detail, check_downloaded_image, restruct_detail_context_data
from .views import resturct_to_place_detail, add_post, post_comment, like_comment_view, like_post
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Review, TripPlan, CategoryPlan, PlaceDetail, PlaceReview, PlaceReviewLike
from django.db import models
from .forms import TripPlanImageForm, TripPlanForm, ReviewForm
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
import json


class PlaceDetailsViewTest(TestCase):
    """Test for place details page."""

    def setUp(self):
        """Initialize API key from env."""
        self.frontend_api_key = config('FRONTEND_API_KEY')
        self.backend_api_key = config('BACKEND_API_KEY')

    def test_invalid_place_id(self):
        """Test viewing place details page with invalid place_id."""
        response = self.client.get(reverse('trip:place-detail', args=['123']))
        self.assertEqual(response.status_code, 404)

    def test_get_details_function(self):
        """Test for get_details_context() function."""
        mock_data = {
            "result": {
                'place_id': '123456',
                'name': "Tawan Boonma",
                'formatted_phone_number': "191",
                'website': "tawanb.dev",
                'rating': 4.4,
                'photos': [{'photo_reference': "1234"}],
                'reviews': [{'author_name': "Tawan", "text": "Good"},
                            {'author_name': "Unknown", "text": ""}],
                'geometry': {'location': {'lat': 10, 'lng': 10}},
                'types': ['school']
            }
        }
        context = get_details_context(
            mock_data, self.backend_api_key, self.frontend_api_key)
        self.assertEqual("Tawan Boonma", context['place_name'])
        self.assertEqual("191", context['phone'])
        self.assertEqual("tawanb.dev", context['website'])
        self.assertEqual(4, context['rating'])
        self.assertEqual(1, context['blank_rating'])
        self.assertIn("1234", context['images'])
        self.assertEqual(1, len(context['reviews']))
        self.assertEqual('123456', context['place_id'])
        self.assertEqual(['school'], context['types'])
        self.assertIsInstance(context['suggestions'], list)

    def test_get_details_function_dont_have_data(self):
        """Test for get_details_context() function."""
        mock_data = {
            "result": {
                'geometry': {'location': {'lat': 10, 'lng': 10}}
            }
        }
        context = get_details_context(
            mock_data, self.backend_api_key, self.frontend_api_key)
        self.assertEqual("N/A", context['place_name'])
        self.assertEqual("N/A", context['phone'])
        self.assertEqual("N/A", context['website'])
        self.assertEqual(0, context['rating'])
        self.assertEqual(0, context['blank_rating'])
        self.assertEqual([], context['images'])
        self.assertEqual(0, len(context['reviews']))
        self.assertIsInstance(context['suggestions'], list)

    def test_empty_get_details_function(self):
        """Test for get_details_context() function with empty place_data."""
        context = get_details_context(
            {}, self.backend_api_key, self.frontend_api_key)
        self.assertEqual({'api_key': self.frontend_api_key}, context)

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

    def test_check_downloaded_image(self):
        PLACE_IMG_PATH = os.path.join(
            BASE_DIR, 'media', 'places_image')
        if not os.path.exists(PLACE_IMG_PATH):
            os.mkdir(PLACE_IMG_PATH)
        mockup_data = {
            "place_name": "test1",
            "place_id": "test1",
            "images": [
                "test1",
                "test11"
            ],
            "suggestions": [{"place_name": "test2", "photo_ref": "test2", "place_id": "test2"}]
        }
        context = check_downloaded_image(mockup_data)
        self.assertEqual(False, context['downloaded'])
        self.assertEqual(False, context['suggestions'][0]['downloaded'])
        new = open(os.path.join(PLACE_IMG_PATH, 'test1_0photo.jpeg'), 'wb')
        new.close()
        context = check_downloaded_image(mockup_data)
        self.assertEqual(False, context['downloaded'])
        new = open(os.path.join(PLACE_IMG_PATH, 'test1_1photo.jpeg'), 'wb')
        new.close()
        context = check_downloaded_image(mockup_data)
        self.assertEqual(True, context['downloaded'])
        new = open(os.path.join(PLACE_IMG_PATH, 'test2photo.jpeg'), 'wb')
        new.close()
        context = check_downloaded_image(mockup_data)
        self.assertEqual(True, context["suggestions"][0]['downloaded'])
        os.remove(os.path.join(PLACE_IMG_PATH, 'test1_0photo.jpeg'))
        os.remove(os.path.join(PLACE_IMG_PATH, 'test1_1photo.jpeg'))
        os.remove(os.path.join(PLACE_IMG_PATH, 'test2photo.jpeg'))
        mockup_data = {
            "place_name": "test1",
            "place_id": "test1",
            "images": [
                "test1",
            ],
            "suggestions": [{"place_name": "test2", "photo_ref": "test2", "place_id": "test2"}]
        }
        context = check_downloaded_image(mockup_data)
        self.assertEqual(False, context['downloaded'])
        new = open(os.path.join(PLACE_IMG_PATH, 'test1photo.jpeg'), 'wb')
        new.close()
        context = check_downloaded_image(mockup_data)
        self.assertEqual(True, context['downloaded'])
        os.remove(os.path.join(PLACE_IMG_PATH, 'test1photo.jpeg'))

    def test_restruct_detail_context_data(self):
        mockup_data = {
            "place_name": "test1",
            "place_id": "test1",
            "images": ["test1"],
            "reviews": [{"author": "- - SHJR", "text": "It was perfect"}],
            "types": ["lodging"],
            "phone": "11223344",
            "rating": 4,
            "blank_rating": 1,
            "website": "www.ku.ac.th",
            "suggestions": [{"place_name": "test2", "photo_ref": "test2", "place_id": "test2"}]
        }
        self.assertEqual(2, len(restruct_detail_context_data(mockup_data)))

    def test_resturct_to_place_detail(self):
        mockup_data = [
            {
                "place_name": "The tr",
                "place_id": "ChIJBaF",
                "photo_ref": [
                    "Aap_uECILxxdbdn"
                ],
                "types": ["lodging"],
                "reviews": [{"author": "- - SHJR", "text": "It was perfect"}],
                "phone": "1111111",
                "rating": 4,
                "blank_rating": 1,
                "website": "threpose"
            },
            {
                "place_name": "Ban",
                "photo_ref": "A",
                "place_id": "ChIJae"
            }
        ]
        expected_data = {
            'place_name': 'The tr',
            'place_id': 'ChIJBaF',
            'types': [['lodging']],
            'rating': 4,
            'blank_rating': 1,
            'images': ['Aap_uECILxxdbdn'],
            'google_reviews': [{'author': '- - SHJR', 'text': 'It was perfect'}],
            'suggestions': [{'place_name': 'Ban', 'photo_ref': 'A', 'place_id': 'ChIJae'}],
            'website': 'threpose',
            'phone': '1111111'
        }
        context = resturct_to_place_detail(mockup_data)
        self.assertEqual(expected_data, context)


class IndexViewTest(TestCase):
    """Test for index page."""

    def setUp(self):
        """Initialize user and trips."""
        self.user = User.objects.create_user(
            username='tester', password='tester')
        self.user.save()
        self.client = Client()
        self.client.login(username='tester', password='tester')

    def test_response(self):
        """Test response for directing index page."""
        response = self.client.get(reverse('trip:index'))
        self.assertEqual(response.status_code, 200)

    def test_get_trip_queries(self):
        """Test queries response form server."""
        trip = TripPlan.objects.create(
            title='test', body='create_trip', author=self.user, duration=1, price=1, complete=True)
        trip.save()
        # input starting letters of trip.
        response = self.client.post(reverse("trip:get-trip-query"),
                                    {"keyword": json.dumps("te")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], "OK")
        self.assertEqual(len(json.loads(response.content)["results"]), 1)

    def test_invalid_get_trip_queries(self):
        """Test queries response form server with invalid payload."""
        trip = TripPlan.objects.create(title='test', body='create_trip', author=self.user,
                                       duration=1, price=1, complete=True)
        trip.save()
        # input starting letters of trip.
        response = self.client.post(reverse("trip:get-trip-query"),
                                    {"k": json.dumps("te")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], "BAD_REQUEST")


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
        self.re = RequestFactory()
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
        self.assertEqual(TripPlan.objects.filter(id='1')[0].total_like, 1)

    def test_like_more_than_one_user(self):
        """Test have more than one user like same post."""
        self.user2 = self.user = User.objects.create(
            username='tester2', password='tester2')
        post = get_object_or_404(TripPlan, id='1')
        post.like.add(self.user)
        post.like.add(self.user2)
        self.assertEqual(TripPlan.objects.filter(id='1')[0].total_like, 1)

    def test_dont_count_like_by_same_user(self):
        """Test post like not count user like if same user."""
        post = get_object_or_404(TripPlan, id='1')
        post.like.add(self.user)
        post.like.add(self.user)
        self.assertEqual(TripPlan.objects.filter(id='1')[0].total_like, 1)

    def test_cant_delete_category_when_have_post_in_category(self):
        """Test Protect from category."""
        with self.assertRaises(models.ProtectedError):
            CategoryPlan.objects.filter(name='category1').delete()

    def tearDown(self):
        """Reset all user, all category and all tripplan."""
        User.objects.all().delete()
        TripPlan.objects.all().delete()
        CategoryPlan.objects.all().delete()
        return super().tearDown()


class AddPostTests(TestCase):
    """Class for test add)post method."""

    def setUp(self):
        """Set up trip, user and category."""
        self.client = Client()
        self.cat = CategoryPlan.objects.create(name='category1')
        self.user = User.objects.create(username='tester', password='tester')
        self.trip = TripPlan.objects.create()
        self.re = RequestFactory()
        return super().setUp()

    def test_first_add_post(self):
        """Test add_post method."""
        request = self.re.get('/addpost/')
        request.user = self.user
        self.assertEqual(add_post(request).status_code, 200)

    def test_add_post_method_post(self):
        self.client.force_login(self.user)
        info = {'title': 'test', 'duration': '0',
                         'price': '1', 'category': 'category1', 'body': 'test',
                         'post_date': timezone.now(), 'like': '', 'complete': 'False'}
        response = self.client.post(reverse('trip:addpost'), data=info)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        """Reset all user, all category and all tripplan."""
        User.objects.all().delete()
        TripPlan.objects.all().delete()
        CategoryPlan.objects.all().delete()
        return super().tearDown()


class TripDetailTests(TestCase):
    """Class for test trip detail method."""

    def setUp(self):
        """Set up trip, user and category."""
        self.client = Client()
        self.cat = CategoryPlan.objects.create(name='category1')
        self.user = User.objects.create(username='tester', password='tester')
        self.trip = TripPlan.objects.create()
        self.re = RequestFactory()
        return super().setUp()

    def test_access_trip_detail(self):
        """Test trip detail method."""
        request = self.re.get('tripdetail/1/')
        request.user = self.user
        self.assertEqual(trip_detail(request, 1).status_code, 200)

    def test_create_review_in_trip_detail(self):
        """Test post method of trip detail."""
        self.client.force_login(self.user)
        self.client.get('tripdetail/1/')
        form_data = {'post': self.trip, 'name': self.user, 'body': 'test'}
        review = ReviewForm(data=form_data)
        self.assertTrue(review.is_valid())
        response = self.client.post(
            reverse('trip:tripdetail', args=['1']), data={'form': form_data})
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        """Reset all user, all category and all tripplan."""
        User.objects.all().delete()
        TripPlan.objects.all().delete()
        CategoryPlan.objects.all().delete()
        return super().tearDown()


class DeletePostlTests(TestCase):
    """Class for test trip detail method."""

    def setUp(self):
        """Set up trip, user and category."""
        self.client = Client()
        self.cat = CategoryPlan.objects.create(name='category1')
        self.user = User.objects.create(username='tester', password='tester')
        self.user.active = True
        self.trip = TripPlan.objects.create()
        self.re = RequestFactory()
        return super().setUp()

    def test_access_delete_post(self):
        """Test delete post method."""
        request = self.re.get('tripdetail/1/remove')
        request.user = self.user
        self.assertEqual(delete_post(request, 1).status_code, 200)

    def tearDown(self):
        """Reset all user, all category and all tripplan."""
        User.objects.all().delete()
        TripPlan.objects.all().delete()
        CategoryPlan.objects.all().delete()
        return super().tearDown()


@unittest.skip
class SeleniumTripPlan(LiveServerTestCase):
    """Classs for test selenium"""

    def setUp(self) -> None:
        """Set up user."""
        self.user = User.objects.create(username='tester', password='tester')
        self.user.active = True

    def test_create_trip(self):
        """Test user create trip."""
        browser = webdriver.Chrome('selenium/chromedriver.exe')
        browser.get("http://127.0.0.1:80/accounts/login")
        input = browser.find_elements_by_tag_name("input")
        username = input[1]
        password = input[2]
        username.send_keys('demo')
        password.send_keys('pass12345')
        login = browser.find_elements_by_tag_name("button")[1]
        login.click()
        browser.get("http://127.0.0.1:80/addpost/")
        browser.find_element(By.NAME, "title").send_keys("test")
        browser.find_element(By.NAME, "duration").send_keys(1)
        browser.find_element(By.NAME, "price").send_keys(1)
        button = browser.find_elements_by_tag_name("button")[3]
        button.click()
        assert 'test' in browser.page_source
        assert '1' in browser.page_source

    def tearDown(self) -> None:
        """Reset all user."""
        User.objects.all().delete()
        return super().tearDown()


class PlaceDetailModelTest(TestCase):
    """Tests for PlaceDetail model."""

    def setUp(self):
        """Initialize user and place detail."""
        self.reviewed_user_data = {
            "username": "Tester", "password": "ThaiRepose"}
        self.reviewed_user = User.objects.create_user(username=self.reviewed_user_data['username'],
                                                      password=self.reviewed_user_data['password'])
        self.reviewed_user.save()
        self.client = Client()
        self.client.login(username=self.reviewed_user_data['username'],
                          password=self.reviewed_user_data['password'])
        self.blog = TripPlan.objects.create(title='test', body='create_trip', author=self.reviewed_user,
                                            duration=1, price=1, complete=True)
        self.blog.save()
        self.place_id = "Qwerty123456"
        self.place = PlaceDetail.objects.create(
            name="NewPlace", place_id=self.place_id)

    def test_post_review(self):
        """Test that user can review a place properly."""
        review_text = "This is a good place!"
        response = self.client.post(reverse("trip:place-review", args=[self.place_id]),
                                    {"review": review_text})
        # redirect to place detail page
        self.assertEqual(response.status_code, 302)
        # Check that review has been added to correct place.
        self.place.placereview_set.get(
            author=self.reviewed_user, place__place_id=self.place_id)

    def test_review_like(self):
        """Test that user can like review for 1 unit."""
        review_text = "This is a good place!"
        self.client.post(reverse("trip:place-review", args=[self.place_id]),
                         {"review": review_text})
        review = self.place.placereview_set.get(
            author=self.reviewed_user, place__place_id=self.place_id)
        response = self.client.post(reverse("trip:place-like", args=[self.place_id]),
                                    {"review_id": review.id})
        # redirect to the detail page.
        self.assertEqual(response.status_code, 302)
        # get new review detail
        review = self.place.placereview_set.get(
            author=self.reviewed_user, place__place_id=self.place_id)
        self.assertEqual(review.likes, 1)
        self.assertEqual(review.dislikes, 0)

    def test_review_dislike(self):
        """Test that user can dislike a review place for 1 unit."""
        review_text = "This is a nice place!"
        self.client.post(reverse("trip:place-review", args=[self.place_id]),
                         {"review": review_text})
        review = self.place.placereview_set.get(
            author=self.reviewed_user, place__place_id=self.place_id)
        response = self.client.post(reverse("trip:place-dislike", args=[self.place_id]),
                                    {"review_id": review.id})
        # redirect to the detail page.
        self.assertEqual(response.status_code, 302)
        # get new review detail
        review = self.place.placereview_set.get(
            author=self.reviewed_user, place__place_id=self.place_id)
        self.assertEqual(review.dislikes, 1)
        self.assertEqual(review.likes, 0)

    def test_unlike(self):
        """Test in case that user click like again, should remove like."""
        review_text = "This is a nice place!"
        self.client.post(reverse("trip:place-review", args=[self.place_id]),
                         {"review": review_text})
        review = self.place.placereview_set.get(
            author=self.reviewed_user, place__place_id=self.place_id)
        self.client.post(reverse("trip:place-like", args=[self.place_id]),
                         {"review_id": review.id})
        self.client.post(reverse("trip:place-like", args=[self.place_id]),
                         {"review_id": review.id})
        review = self.place.placereview_set.get(
            author=self.reviewed_user, place__place_id=self.place_id)
        self.assertEqual(review.dislikes, 0)
        self.assertEqual(review.likes, 0)

    def test_remove_dislike(self):
        """Test in case that user click dislike again, should remove dislike."""
        review_text = "This is a nice place!"
        self.client.post(reverse("trip:place-review", args=[self.place_id]),
                         {"review": review_text})
        review = self.place.placereview_set.get(
            author=self.reviewed_user, place__place_id=self.place_id)
        self.client.post(reverse("trip:place-dislike", args=[self.place_id]),
                         {"review_id": review.id})
        self.client.post(reverse("trip:place-dislike", args=[self.place_id]),
                         {"review_id": review.id})
        review = self.place.placereview_set.get(
            author=self.reviewed_user, place__place_id=self.place_id)
        self.assertEqual(review.dislikes, 0)
        self.assertEqual(review.likes, 0)

    def test_like_dislike_invalid_method(self):
        """Test like/dislike with method isn't POST, should redirect to place detail page without doing any like."""
        review_text = "This is a good place!"
        self.client.post(reverse("trip:place-review", args=[self.place_id]),
                         {"review": review_text})
        review = self.place.placereview_set.get(
            author=self.reviewed_user, place__place_id=self.place_id)
        response1 = self.client.get(reverse("trip:place-dislike", args=[self.place_id]),
                                    {"review_id": review.id})
        response2 = self.client.get(reverse("trip:place-dislike", args=[self.place_id]),
                                    {"review_id": review.id})
        # All response should return redirect
        self.assertEqual(response1.status_code, 302)
        self.assertEqual(response2.status_code, 302)
        review = self.place.placereview_set.get(
            author=self.reviewed_user, place__place_id=self.place_id)
        self.assertEqual(review.dislikes, 0)
        self.assertEqual(review.likes, 0)


class TestPostComment(TestCase):
    """Class for test post comment"""

    def setUp(self) -> None:
        self.user = User.objects.create(username='tester', password='tester')
        post = TripPlan.objects.create()
        post.save()
        self.user.active = True
        self.rf = RequestFactory()
        self.rf.user = self.user
        self.rf.method = 'POST'
        self.rf.POST = {'pk': 1, 'comment': '123'}

    def test_post_comment(self):
        """Test post comment success"""
        response = post_comment(self.rf)
        self.assertEqual(response.status_code, 200)

    def test_fail_post_comment(self):
        """Test post comment fail"""
        self.rf.method = 'GET'
        self.assertIsNone(post_comment(self.rf))

    def tearDown(self):
        """Reset all user, all category and all tripplan."""
        User.objects.all().delete()
        TripPlan.objects.all().delete()
        return super().tearDown()


class TestLike(TestCase):
    """Class for test like function"""

    def setUp(self):
        self.user = User.objects.create(username='tester', password='tester')
        post = TripPlan.objects.create()
        comment = Review.objects.create(name=self.user, post=post)
        post.save()
        comment.save()
        self.rf = RequestFactory()
        self.rf.user = self.user
        self.rf.method = 'POST'
        self.rf.POST = {'pk': 1, 'comment_id': comment.id}
        post.save()

    def test_like_unlike_post(self):
        response = like_post(self.rf)
        self.assertEqual(response.status_code, 200)
        response = like_post(self.rf)
        self.assertEqual(response.status_code, 200)

    def test_like_unlike_comment(self):
        response = like_comment_view(self.rf)
        self.assertEqual(response.status_code, 200)
        response = like_comment_view(self.rf)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        """Reset all user, all category and all tripplan."""
        User.objects.all().delete()
        TripPlan.objects.all().delete()
        Review.objects.all().delete()
        return super().tearDown()


class TestAddPost(TestCase):
    """Class for test add post function"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='tester', password='tester')
        email_model = EmailAddress.objects.create(
            user=self.user, verified=True)
        email_model.save()
        self.user.save()
        self.rf = RequestFactory()
        self.rf.user = self.user
        self.rf.method = 'POST'

    def test_create_first_plan(self):
        self.client.force_login(self.user)
        info = {'title': 'test', 'duration': 1,
                         'price': 1, 'category': 'category1', 'body': 'test',
                         'post_date': timezone.now(), 'like': '', 'complete': 'False'}
        response = self.client.post(reverse('trip:addpost'), data=info)
        self.assertEqual(response.status_code, 200)

    def test_create_second_blog(self):
        trip = TripPlan.objects.create(author=self.user, complete=False)
        trip.save()
        self.client.force_login(self.user)
        info = {'title': 'test', 'duration': 1,
                         'price': 1, 'body': 'test',
                         'post_date': timezone.now(), 'like': '', 'complete': 'False', 'blog': '123'}
        response = self.client.post(reverse('trip:addpost'), data=info)
        self.assertEqual(response.status_code, 302)

    def test_create_second_save_blog(self):
        trip = TripPlan.objects.create(author=self.user, complete=False)
        trip.save()
        self.client.force_login(self.user)
        info = {'title': 'test', 'duration': 1,
                         'price': 1, 'body': 'test',
                         'post_date': timezone.now(), 'like': '', 'complete': 'False', 'save_blog': '100101'}
        response = self.client.post(reverse('trip:addpost'), data=info)
        self.assertEqual(response.status_code, 200)

    def test_create_second_imgpic(self):
        trip = TripPlan.objects.create(author=self.user, complete=False)
        trip.save()
        self.client.force_login(self.user)
        info = {'title': 'test', 'duration': 1,
                         'price': 1, 'body': 'test',
                         'post_date': timezone.now(), 'like': '', 'complete': 'False', 'imgpic': '100101'}
        response = self.client.post(reverse('trip:addpost'), data=info)
        self.assertEqual(response.status_code, 200)

    def test_empty_body(self):
        trip = TripPlan.objects.create(author=self.user, complete=False)
        trip.save()
        self.client.force_login(self.user)
        info = {'title': 'test', 'duration': 1,
                         'price': 1, 'body': '',
                         'post_date': timezone.now(), 'like': '', 'complete': 'False', 'blog': '123'}
        response = self.client.post(reverse('trip:addpost'), data=info)
        self.assertEqual(response.status_code, 200)

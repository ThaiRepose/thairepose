import os

from django.test import TestCase, RequestFactory
from django.urls.base import reverse
from threpose.settings import BASE_DIR
from .views import get_next_page_from_token
from .views import restruct_nearby_place
from .views import add_more_place
from .views import check_downloaded_image


class GetNextPageTest(TestCase):
    """test get next page data from frontend"""

    def setUp(self):
        """Set up trip plan for create review"""
        self.factory = RequestFactory()

    def test_post_request_fail(self):
        """Post request with out token"""
        request = self.factory.post(reverse('search:next-place-list'), {}, content_type='application/json')
        response = get_next_page_from_token(request)
        self.assertEqual(str(response.content, encoding='utf8'), '{"status": "INVALID PAYLOAD"}')

    def test_get_request_fail(self):
        """get request to next-page-list"""
        request = self.factory.get(reverse('search:next-place-list'), {}, content_type='application/json')
        response = get_next_page_from_token(request)
        self.assertEqual(str(response.content, encoding='utf8'), '{"status": "INVALID METHOD"}')


class PlaceListTest(TestCase):
    """test place list"""
    def setUp(self):
        """Set up trip plan for create review"""
        self.factory = RequestFactory()

    def test_restruct_nearby_place(self):
        test_data = [
            {
                'name': 'test1',
                'place_id': '11223344',
                'types': ['school', 'workspace'],
                'something1': 'hi',
                'something2': 'hi there'},
            {
                'name': 'test1',
                'place_id': '11223344',
                'photos': [{'photo_reference': 12345678910}],
                'types': ['school', 'workspace'],
                'something1': 'hi',
                'something2': 'hi there'
            }
        ]
        expect_outcome = [
            {
                'place_name': 'test1',
                'place_id': '11223344',
                'photo_ref': [12345678910],
                'types': ['school', 'workspace']
            }
        ]
        data = restruct_nearby_place(test_data)
        self.assertEqual(expect_outcome, data)

    def test_add_more_place(self):
        context = []
        new1 = [
            {
                'name': 'test1',
                'place_id': '11223344',
                'types': ['school', 'workspace'],
                'something1':'hi',
                'something2':'hi there'
            }
        ]
        new2 = [
            {
                'name': 'test2',
                'place_id': '11223355',
                'photos': [{'photo_reference': 12345678999}],
                'types': ['school', 'workspace'],
                'something1': 'hi',
                'something2': 'hi there'
            }
        ]
        context = add_more_place(context, new1)
        self.assertEqual(context, new1)
        context = add_more_place(context, new2)
        self.assertEqual(context, new1 + new2)
        context = add_more_place(context, new2)
        self.assertEqual(context, new1 + new2)

    def test_check_downloaded_image(self):
        PLACE_IMG_PATH = os.path.join(BASE_DIR, 'theme', 'static', 'images', 'places_image')
        context = [{
            'name': 'test1',
            'place_id': '11223344',
            'types': ['school', 'workspace'],
            'photo_ref': [12345678910],
            'something1':'hi',
            'something2':'hi there'
        }]
        if not os.path.exists(PLACE_IMG_PATH):
            os.mkdir(PLACE_IMG_PATH)
        context = check_downloaded_image(context)
        self.assertEqual(False, context[0]['downloaded'])
        new = open(os.path.join(PLACE_IMG_PATH, "11223344photo.jpeg"), 'wb')
        new.close()
        context = check_downloaded_image(context)
        self.assertEqual(True, context[0]['downloaded'])
        os.remove(os.path.join(PLACE_IMG_PATH, "11223344photo.jpeg"))

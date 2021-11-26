from django.test import TestCase
from django.urls import reverse


class PagesViewTest(TestCase):
    """Test that pages are able to open."""

    def test_about_us(self):
        """Test that about us is linked to namespace."""
        response = self.client.get(reverse("about-us"))
        self.assertEqual(response.status_code, 200)

    def test_feedback(self):
        """That that feedback page is linked to namespace."""
        response = self.client.get(reverse("feedback"))
        self.assertEqual(response.status_code, 200)

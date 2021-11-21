from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Plan, Editor, Place
import datetime


class EditViewTest(TestCase):
    """Initialize setUp for all Edit and View Planner testing."""

    def setUp(self):
        """Initialize user and a plan."""
        self.client = Client()
        self.username = "TawanBoonma"
        self.password = "Thairepose"
        self.email = "thairepose@mail.com"
        self.user = User.objects.create_user(username=self.username,
                                             email=self.email,
                                             password=self.password)
        self.user.save()
        self.plan = Plan.objects.create(name="Test", days=2, author=self.user)
        self.plan.save()
        self.client.login(username=self.username, password=self.password)


class AuthorEditViewTest(EditViewTest):
    """Tests for author planner can edit correctly."""

    def test_author_edit_planner(self):
        """Test author can edit his owned planner."""
        response = self.client.get(reverse("planner:edit_plan", args=[self.plan.id]))
        self.assertEqual(response.status_code, 200)

    def test_author_view_planner(self):
        """Test author can view his owned planner."""
        response = self.client.get(reverse("planner:view_plan", args=[self.plan.id]))
        self.assertEqual(response.status_code, 200)


class EditorEditViewTest(EditViewTest):
    """Tests for author planner can edit correctly."""

    def setUp(self):
        """Initialize editor user."""
        super().setUp()
        self.editor_username = "ThaiRepose2"
        self.editor_password = "TawanBoonma"
        editor_user = User.objects.create_user(username=self.editor_username,
                                               email=self.email,
                                               password=self.editor_password)
        self.editor = Editor.objects.create(plan=self.plan, user=editor_user, role=1)
        self.editor_client = Client()
        self.editor_client.login(username=self.editor_username, password=self.editor_password)

    def test_editor_edit_planner(self):
        """Test access edit planner with editor role."""
        response = self.editor_client.get(reverse('planner:edit_plan', args=[self.plan.id]))
        self.assertEqual(response.status_code, 200)

    def test_editor_view_planner(self):
        """Test access edit planner with editor role."""
        response = self.editor_client.get(reverse('planner:view_plan', args=[self.plan.id]))
        self.assertEqual(response.status_code, 200)


class AnonymousEditViewTest(EditViewTest):
    """Test for not authenticated user and normal user accessing planner editor."""

    def setUp(self):
        """Setup normal user which doesn't have any permission to current plan."""
        super().setUp()
        self.new_user_username = "ThaiRepose2"
        self.new_user_password = "TawanBoonma"
        self.new_user = User.objects.create_user(username=self.new_user_username,
                                                 email=self.email,
                                                 password=self.new_user_password)
        self.new_user_client = Client()
        self.new_user_client.login(username=self.new_user_username, password=self.new_user_password)

    def test_edit_plan_without_login(self):
        """Test going to edit planner page without any.
        Should redirect to view planner page and returned 404 because of PRIVATE planner.
        """
        self.client.logout()
        response = self.client.get(reverse('planner:edit_plan', args=[self.plan.id]))
        self.assertRedirects(response,
                             reverse("planner:view_plan", args=[self.plan.id]),
                             status_code=302,
                             target_status_code=404,  # should return 404 because of not authenticated.
                             fetch_redirect_response=True)  # should redirect to view planner.

    def test_edit_private_plan_without_perm(self):
        """Test going to edit planner with permission of VIEWER.
        Should redirect to view planner page and returned 200.
        """
        Editor.objects.create(user=self.new_user, plan=self.plan)
        response = self.new_user_client.get(reverse('planner:edit_plan', args=[self.plan.id]))
        self.assertRedirects(response,
                             reverse("planner:view_plan", args=[self.plan.id]),
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)  # should redirect to view planner.

    def test_view_private_plan_without_perm(self):
        """Test viewing the private plan without any permission."""
        response = self.new_user_client.get(reverse('planner:view_plan', args=[self.plan.id]))
        self.assertEqual(response.status_code, 404)

    def test_view_private_plan_with_perm(self):
        """Test viewing the private plan with permission of VIEWER."""
        Editor.objects.create(user=self.new_user, plan=self.plan)
        response = self.new_user_client.get(reverse('planner:view_plan', args=[self.plan.id]))
        self.assertEqual(response.status_code, 200)

    def test_edit_public_plan_without_auth(self):
        """Test editing the private plan without any authentication.
        Should redirect to view page.
        """
        self.client.logout()
        self.plan.status = 1  # change the plan to be public
        self.plan.save()
        response = self.client.get(reverse('planner:edit_plan', args=[self.plan.id]))
        self.assertRedirects(response,
                             reverse("planner:view_plan", args=[self.plan.id]),
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)  # should redirect to view planner.

    def test_view_public_plan_without_auth(self):
        """Test editing the private plan without any authentication.
        Should redirect to view page.
        """
        self.plan.status = 1  # change the plan to be public
        self.plan.save()
        response = self.client.get(reverse('planner:view_plan', args=[self.plan.id]))
        self.assertEqual(response.status_code, 200)


class ViewOnlyTest(EditViewTest):
    """Testing viewing view-only planner."""
    
    def setUp(self):
        """Initialize place."""
        super().setUp()
        self.place_details1 = {
            'day': 1,
            'sequence': 1,
            'place_id': "5678",
            'place_name': "Kasetsart",
            'place_vicinity': "Bangkok"
        }
        self.place1 = Place.objects.create(day=self.place_details1['day'],
                                           sequence=self.place_details1['sequence'],
                                           place_id=self.place_details1['place_id'],
                                           place_name=self.place_details1['place_name'],
                                           place_vicinity=self.place_details1['place_vicinity'],
                                           departure_time=datetime.time(0, 0),
                                           plan=self.plan)
        self.place1.save()

    def test_view_only_page(self):
        """Test that view-only page show places in the plan."""
        response = self.client.get(reverse('planner:view_plan', args=[self.plan.id]))
        self.assertContains(response, self.place1)

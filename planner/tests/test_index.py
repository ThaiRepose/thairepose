from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.http import urlencode

from ..models import Plan, Editor


class ViewTest(TestCase):
    """Initialize setUp for all View testing."""

    def setUp(self):
        """Initialize user and a plan."""
        self.client = Client()
        self.username = "ThaiRepose"
        self.password = "TawanBoonma"
        self.email = "thairepose@mail.com"
        self.user = User.objects.create_user(username=self.username,
                                             email=self.email,
                                             password=self.password)
        self.user.save()
        self.plan = Plan.objects.create(name="Test", days=2, author=self.user)
        self.plan.save()
        self.client.login(username=self.username, password=self.password)


class AuthorViewTest(ViewTest):
    """Test for planner index view can display list of planner correctly."""

    def test_planner_index_view(self):
        """Test index view of planner app can display correctly."""
        response = self.client.get(reverse('planner:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.plan)

    def test_create_planner(self):
        """Test create new planner from planner index should redirect to new planner page."""
        last_plan_id = list(Plan.objects.all())[-1].id  # get last plan id to check next new plan
        response = self.client.get(reverse('planner:create'))
        self.assertRedirects(response,
                             reverse("planner:edit_plan", args=[last_plan_id + 1]),
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_remove_planner(self):
        """Test remove a plan from user. The plan should be deleted."""
        response = self.client.get(reverse('planner:delete', args=[self.plan.id]))
        self.assertRedirects(response,
                             reverse("planner:index"),
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)  # should redirect to planner index.
        # Accessing to edit planner page should return 404.
        response = self.client.get(reverse('planner:edit_plan', args=[self.plan.id]))
        self.assertEqual(response.status_code, 404)
        # Accessing to view planner page should return 404.
        response = self.client.get(reverse('planner:view_plan', args=[self.plan.id]))
        self.assertEqual(response.status_code, 404)
        # In index planner should not have the deleted planner showed.
        response = self.client.get(reverse('planner:index'))
        self.assertNotContains(response, self.plan)
        # After removing the removed planner should redirect to planner index without doing anything.
        # By doing this, the consequence should be the same as previous context above.
        previous_context = response.context
        response = self.client.get(reverse('planner:delete', args=[self.plan.id]))
        # should redirect to planner index although there is no plan to be removed.
        self.assertRedirects(response,
                             reverse("planner:index"),
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)
        response = self.client.get(reverse('planner:index'))
        # Plans queries should be the same
        self.assertQuerysetEqual(previous_context['plans'], response.context['plans'])


class EditorViewTest(ViewTest):
    """Tests for editor users."""

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

    def test_editor_planner_index(self):
        """Test index view of planner by editor user."""
        response = self.editor_client.get(reverse('planner:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.plan)

    def test_editor_remove_planner(self):
        """Test that editor remove themselves from the planner that they don't own."""
        response = self.editor_client.get(reverse('planner:delete', args=[self.plan.id]))
        self.assertRedirects(response,
                             reverse("planner:index"),
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)  # should redirect to planner index.
        self.assertNotIn(self.editor, self.plan.editor_set.all())  # editor should not be in the planner.
        # In index planner should not show show the planner even the plan is not deleted from author.
        response = self.editor_client.get(reverse('planner:index'))
        self.assertNotContains(response, self.plan)
        self.assertIn(self.plan, Plan.objects.all())  # The plan still existed in database.


class AnonymousViewTest(ViewTest):
    """Test for not authenticated user and normal user accessing planner index."""

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

    def test_planner_index_without_login(self):
        """Test index view of planner without logged in, should redirect to login page."""
        self.client.logout()
        response = self.client.get(reverse('planner:index'))
        target_redirect = reverse("account_login")
        target_redirect_params = urlencode({'next': reverse('planner:index')})
        self.assertRedirects(response,
                             f"{target_redirect}?{target_redirect_params}",
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

    def test_remove_plan_without_perm(self):
        """Test going to remove a planner without any permission.
        Should done nothing and redirect to index page.
        """
        response = self.new_user_client.get(reverse('planner:delete', args=[self.plan.id]))
        self.assertRedirects(response,
                             reverse("planner:index"),
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)
        self.assertIn(self.plan, Plan.objects.all())

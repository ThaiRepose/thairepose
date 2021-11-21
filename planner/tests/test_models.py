import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Place, Plan, Editor, MAX_DAYS_PER_PLAN


class PlannerModelTest(TestCase):
    """Initialized tests for all method in Planner."""

    def setUp(self):
        """Initialize user and a plan."""
        self.username = "ThaiRepose"
        self.password = "TawanBoonma"
        self.email = "thairepose@mail.com"
        self.planned_days = 2
        self.user = User.objects.create_user(username=self.username,
                                             email=self.email,
                                             password=self.password)
        self.plan = Plan.objects.create(days=self.planned_days, author=self.user)


class PlanModelTest(PlannerModelTest):
    """Tests for plan model using."""

    def setUp(self):
        """Initialize user and a plan."""
        super().setUp()

    def test_model_name(self):
        """Test that object can display name correctly."""
        plan_name = "Test"
        plan = Plan.objects.create(name=plan_name, days=self.planned_days, author=self.user)
        self.assertEqual(plan.__str__(), plan_name)

    def test_is_editable(self):
        """Test is_editable() method in Plan."""
        other_user = User.objects.create_user(username="Guest",
                                              email="guest@mail.com",
                                              password="NewGuest2021")
        self.assertTrue(self.plan.is_editable(self.user))
        self.assertFalse(self.plan.is_editable(other_user))
        self.assertFalse(self.plan.is_editable(None))
        self.assertFalse(self.plan.is_editable(True))
        Editor.objects.create(plan=self.plan, user=other_user, role=1)
        self.assertTrue(self.plan.is_editable(other_user))

    def test_is_viewable(self):
        """Test is_viewable() method in Plan."""
        other_user = User.objects.create_user(username="Guest",
                                              email="guest@mail.com",
                                              password="NewGuest2021")
        self.assertTrue(self.plan.is_viewable(self.user))
        self.assertFalse(self.plan.is_viewable(other_user))
        self.assertFalse(self.plan.is_viewable(None))
        self.assertFalse(self.plan.is_viewable(True))
        Editor.objects.create(plan=self.plan, user=other_user, role=1)
        self.assertTrue(self.plan.is_viewable(other_user))  # Editor user can view plan too.
        self.plan.status = 1
        self.assertTrue(self.plan.is_viewable(None))  # Now everyone should be able to view this plan.

    def test_initial_name(self):
        """Test planner initial name for user who does/doesn't provide first_name."""
        self.assertEqual(self.plan.__str__(), f"{self.username}'s Plan")
        new_user_firstname = "Tawan"
        # create new planner which user has first_name
        new_user = User.objects.create_user(username="ThaiRepose2",
                                            first_name=new_user_firstname,
                                            email=self.email,
                                            password="TawanBoonma2")
        new_plan = Plan.objects.create(author=new_user)
        self.assertEqual(new_plan.__str__(), f"{new_user_firstname}'s Plan")

    def test_create_days_over_limit(self):
        """Test creating planner with days over limited.
        Should be replaced with the maximum days per plan.
        """
        new_plan = Plan.objects.create(days=100, author=self.user)
        new_plan.save()
        new_plan_status = Plan.objects.get(pk=new_plan.id)
        self.assertEqual(new_plan_status.days, MAX_DAYS_PER_PLAN)
        new_plan = Plan.objects.create(days=-100, author=self.user)
        new_plan.save()
        new_plan_status = Plan.objects.get(pk=new_plan.id)
        self.assertEqual(new_plan_status.days, 1)


class EditorModelTest(PlannerModelTest):
    """Test for Editor model using."""

    def setUp(self):
        """Initialize user and a plan."""
        super().setUp()
        self.other_user = User.objects.create_user(username="Guest",
                                                   email="guest@mail.com",
                                                   password="NewGuest2021")
        self.editor = Editor.objects.create(user=self.other_user, plan=self.plan, role=1)

    def test_name_spelling(self):
        """Test that object __str__() output correctly."""
        self.assertEqual(self.editor.__str__(), f"{self.plan} - {self.other_user}")

    def test_add_editor(self):
        """Test add editor to the plan and check editor_set in the plan."""
        editor_user = User.objects.create_user(username="ThaiRepose2",
                                               email=self.email,
                                               password="TawanBoonma")
        editor = Editor.objects.create(plan=self.plan, user=editor_user)
        self.assertIn(editor, self.plan.editor_set.all())


class PlaceModelTest(PlannerModelTest):
    """Test for Place model using."""

    def setUp(self):
        """Initialize user and a plan."""
        super().setUp()
        self.first_place_name = "SIAM"
        self.first_place = Place.objects.create(day=1,
                                                sequence=1,
                                                place_id="PLACE_ID",
                                                place_name=self.first_place_name,
                                                place_vicinity="Bangkok",
                                                arrival_time=None,
                                                departure_time=datetime.time(0, 0, 0),
                                                plan=self.plan)
        self.second_place_name = "CENTRAL"
        self.second_place = Place.objects.create(day=1,
                                                 sequence=2,
                                                 place_id="PLACE_ID2",
                                                 place_name=self.second_place_name,
                                                 place_vicinity="Bangkok2",
                                                 arrival_time=None,
                                                 departure_time=datetime.time(0, 0, 0),
                                                 plan=self.plan)

    def test_locate_place(self):
        """Check order of places in the plan."""
        self.assertIn(self.first_place, self.plan.place_set.all())
        self.assertEqual(self.first_place.sequence, 1)  # sequence starts at 1
        self.assertEqual(self.first_place, self.plan.place_set.all()[0])
        self.assertEqual(self.second_place, self.plan.place_set.all()[1])

    def test_place_spelling(self):
        """Test that object can display place object correctly in string format."""
        self.assertEqual(self.first_place.__str__(), self.first_place_name)

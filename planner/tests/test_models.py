from django.test import TestCase
from .models import Place, Plan, Editor


class PlanModelTest(TestCase):
    """Tests for plan model implementing."""

    def setUp(self):
        """Initialize."""
        pass

    def test_create_plan(self):
        """Test creating 1 planner."""
        self.plan = Plan.objects.create
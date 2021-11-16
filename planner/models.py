from django.core.validators import MaxValueValidator, MinValueValidator
import django.contrib.auth.models
from django.db import models

MAX_DAYS_PER_PLAN = 6
STATUS = (
    (0, 'Private'),
    (1, 'Public')
)
ROLES = (
    (0, 'Viewer'),
    (1, 'Editor')
)


# Create your models here.
class Plan(models.Model):
    """Class for plan organized."""
    name = models.CharField(max_length=250)
    days = models.IntegerField(default=1,
                               validators=[
                                   MaxValueValidator(MAX_DAYS_PER_PLAN),
                                   MinValueValidator(1)
                               ])
    author = models.ForeignKey(django.contrib.auth.models.User, on_delete=models.CASCADE, null=False, blank=False)
    status = models.IntegerField(choices=STATUS, default=0)
    date_created = models.DateTimeField("Date Created", auto_now_add=True, null=False, blank=False)
    last_modified = models.DateTimeField("Last Modified", auto_now=True, null=False, blank=False)

    def __str__(self):
        """Display name for this plan."""
        return self.name


class Editor(models.Model):
    """Class for storing editors for each plan."""
    user = models.ForeignKey(django.contrib.auth.models.User, on_delete=models.CASCADE, null=False, blank=False)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=False, blank=False)
    role = models.IntegerField(choices=ROLES, default=0, null=False, blank=False)

    def __str__(self):
        return f"{self.plan} - {self.user}"


class Place(models.Model):
    """Place in a plan that will be displayed in table."""
    place_id = models.TextField(null=False, blank=False)
    place_name = models.TextField()
    place_vicinity = models.TextField()
    arrival_time = models.TimeField("Arrival")
    departure_time = models.TimeField("Departure")
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)

    def __str__(self):
        return self.place_name

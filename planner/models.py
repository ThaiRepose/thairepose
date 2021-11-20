from django.core.validators import MaxValueValidator, MinValueValidator
import django.contrib.auth.models
from django.db import models

MAX_DAYS_PER_PLAN = 6
MAX_PLACES_PER_DAY = 10
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

    def is_editable(self, user: django.contrib.auth.models.User) -> bool:
        """Returns True if user can edit this plan."""
        if user == self.author:
            return True
        if user in self.editor_set.all():
            return True
        return False

    def is_viewable(self, user: django.contrib.auth.models.User) -> bool:
        """Returns True if someone with link can view this plan."""
        if self.status:
            return True
        if user == self.author:
            return True
        if user in self.editor_set.all():
            return True
        return False


class Editor(models.Model):
    """Class for storing editors for each plan."""
    user = models.ForeignKey(django.contrib.auth.models.User, on_delete=models.CASCADE, null=False, blank=False)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=False, blank=False)
    role = models.IntegerField(choices=ROLES, default=0, null=False, blank=False)

    def __str__(self):
        return f"{self.plan} - {self.user}"


class Place(models.Model):
    """Place in a plan that will be displayed in table."""
    day = models.IntegerField(default=None,
                              validators=[
                                  MaxValueValidator(MAX_DAYS_PER_PLAN),
                                  MinValueValidator(1)
                              ])
    sequence = models.IntegerField(default=None,
                                   validators=[
                                       MaxValueValidator(MAX_PLACES_PER_DAY),
                                       MinValueValidator(1)
                                   ])
    place_id = models.TextField(null=False, blank=False)
    place_name = models.TextField()
    place_vicinity = models.TextField()
    arrival_time = models.TimeField("Arrival", default=None, null=True, blank=True)
    departure_time = models.TimeField("Departure")
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, default=None)

    class Meta:
        ordering = ('day', 'sequence',)

    def __str__(self):
        return self.place_name

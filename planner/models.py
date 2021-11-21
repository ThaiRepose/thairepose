from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

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


class Plan(models.Model):
    """Class for plan organized."""
    name = models.CharField(max_length=250, default=None, null=True)
    days = models.IntegerField(default=1,
                               validators=[
                                   MaxValueValidator(MAX_DAYS_PER_PLAN),
                                   MinValueValidator(1)
                               ])
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    status = models.IntegerField(choices=STATUS, default=0)
    date_created = models.DateTimeField("Date Created", auto_now_add=True, null=False, blank=False)
    last_modified = models.DateTimeField("Last Modified", auto_now=True, null=False, blank=False)

    def __str__(self):
        """Display name for this plan."""
        return self.name

    def is_editable(self, user: User) -> bool:
        """Returns True if user can edit this plan."""
        if user == self.author:
            return True
        try:
            Editor.objects.get(plan=self, user=user, role=1)
            return True
        except ObjectDoesNotExist:
            return False

    def is_viewable(self, user: User) -> bool:
        """Returns True if someone with link can view this plan."""
        if self.status:
            return True
        if user == self.author:
            return True
        try:
            Editor.objects.get(plan=self, user=user)
            return True
        except ObjectDoesNotExist:
            return False


class Editor(models.Model):
    """Class for storing editors for each plan."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
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


@receiver(post_save, sender=Plan)
def my_handler(**kwargs):
    """Initialize planner name if not specified."""
    if kwargs['instance'].name is None or len(kwargs['instance'].name) == 0:
        if kwargs['instance'].author.first_name == "":
            kwargs['instance'].name = kwargs['instance'].author.username + "'s Plan"
        else:
            kwargs['instance'].name = kwargs['instance'].author.first_name + "'s Plan"

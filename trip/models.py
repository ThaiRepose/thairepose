from django.db import models 
from django.contrib.auth.models import User

class TripPlan(models.Model):
    """Class to create field for user input."""
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    body = models.TextField()

    def __str__(self):
        return self.title + ' | ' + str(self.author)


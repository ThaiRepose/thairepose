from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    """model for customer"""
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    username = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=200, null=True)
    surname = models.CharField(max_length=200, null=True)
    birthday = models.DateField(null=True, auto_now=False, auto_now_add=False) 
    is_email_verified = models.BooleanField(default=False, null=True)
    profile_pic = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.username
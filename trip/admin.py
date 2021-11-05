from django.contrib import admin
from .models import TripPlan, Review, CategoryTrip

admin.site.register(TripPlan)
admin.site.register(CategoryTrip)
admin.site.register(Review)

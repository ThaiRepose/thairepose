from django.contrib import admin
from .models import TripPlan, Review, CategoryPlan

admin.site.register(TripPlan)
admin.site.register(CategoryPlan)
admin.site.register(Review)

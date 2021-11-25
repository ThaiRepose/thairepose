from django.contrib import admin
from .models import TripPlan, Review, CategoryPlan, UploadImage
from mptt.admin import MPTTModelAdmin

admin.site.register(TripPlan)
admin.site.register(CategoryPlan)
admin.site.register(Review, MPTTModelAdmin)
admin.site.register(UploadImage)

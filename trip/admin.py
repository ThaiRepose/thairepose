from django.contrib import admin
from .models import TripPlan, Review, CategoryPlan, UploadImage, PlaceDetail, PlaceReview
from mptt.admin import MPTTModelAdmin


class ReviewInline(admin.StackedInline):
    """Admin configuration inline for place review."""

    model = PlaceReview
    extra = 1
    fieldsets = [
        (None, {"fields": ['author', 'review_text']})
    ]


class PlaceDetailAdmin(admin.ModelAdmin):
    """Admin configuration for PlaceDetail."""

    fieldsets = [
        (None, {"fields": ['name', 'place_id']})
    ]
    inlines = [ReviewInline]
    search_fields = ['name']


admin.site.register(TripPlan)
admin.site.register(CategoryPlan)
admin.site.register(Review, MPTTModelAdmin)
admin.site.register(UploadImage)
admin.site.register(PlaceDetail, PlaceDetailAdmin)

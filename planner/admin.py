from django.contrib import admin
from .models import *


class EditorInline(admin.StackedInline):
    """Display inline of editors in admin page."""

    model = Editor
    extra = 2
    fieldsets = [
        (None, {"fields": ['user', 'role']})
    ]


class PlaceInline(admin.StackedInline):
    """Display inline of places in admin page."""

    model = Place
    extra = 1
    fieldsets = [
        (None, {"fields": ['place_id', 'place_name', 'place_vicinity', 'departure_time']})
    ]


class PlanAdmin(admin.ModelAdmin):
    """Custom plan list in admin page."""

    fieldsets = [
        (None, {"fields": ['name', 'author', 'status']})
    ]
    inlines = [EditorInline, PlaceInline]
    list_display = ('name', 'author', 'status', 'date_created', 'last_modified')
    list_filter = ['author', 'status', 'date_created', 'last_modified']
    search_fields = ['name']


admin.site.register(Plan, PlanAdmin)

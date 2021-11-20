from django.contrib import admin
from .models import Editor, Plan, Place


class EditorInline(admin.StackedInline):
    """Display inline of editors in admin page."""

    model = Editor
    extra = 1
    fieldsets = [
        (None, {"fields": ['user', 'role']})
    ]


class PlaceInline(admin.StackedInline):
    """Display inline of places in admin page."""

    model = Place
    extra = 1
    fieldsets = [
        (None, {"fields": ['day', 'sequence', 'place_id', 'place_name',
                           'place_vicinity', 'arrival_time', 'departure_time']})
    ]


class PlanAdmin(admin.ModelAdmin):
    """Custom plan list in admin page."""

    fieldsets = [
        (None, {"fields": ['name', 'days', 'author', 'status']})
    ]
    inlines = [EditorInline, PlaceInline]
    list_display = ('name', 'author', 'status', 'date_created', 'last_modified')
    list_filter = ['author', 'status', 'date_created', 'last_modified']
    search_fields = ['name']


admin.site.register(Plan, PlanAdmin)

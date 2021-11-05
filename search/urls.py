from django.urls import path
from . import views

app_name = 'search'
urlpatterns = [
    path('place-list/', views.place_list, name='place-list'),
]

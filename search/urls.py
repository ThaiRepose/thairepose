from django.urls import path
from . import views

app_name = 'trip'
urlpatterns = [
    path('', views.home, name='home'),
    path('place-list/', views.search, name='search'),
]

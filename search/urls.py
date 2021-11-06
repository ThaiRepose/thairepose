from django.urls import path
from . import views

app_name = 'search'
urlpatterns = [
    path('place-list/', views.place_list, name='place-list'),
    path('get-next-list', views.get_next_page_from_token, name='next-place-list'),
]

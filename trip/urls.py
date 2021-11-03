from django.urls import path
from . import views

app_name = 'trip'
urlpatterns = [
    path('', views.index, name='index'),
    # 127.0.0.1/domnfoironkwe_0394
    path('place/<str:place_id>/', views.place_info, name='place')
]

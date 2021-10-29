from django.urls import path
from . import views

app_name = 'trip'
urlpatterns = [
    path('', views.index, name='index'),
    path('tripplan', views.HomeView.as_view(), name="tripplan"),
    path('tripdetail/<int:pk>', views. DetailView.as_view(), name="tripdetail"),
]

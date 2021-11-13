from django.urls import path
from . import views

app_name = 'trip'
urlpatterns = [
    path('', views.index, name='index'),
    path('tripplan/', views.AllTrip.as_view(), name="tripplan"),
    path('tripdetail/<int:pk>/', views.TripDetail.as_view(), name="tripdetail"),
    path('addpost/', views.AddPost.as_view(), name="addpost"),
    path('tripdetail/<int:pk>/addreview/', views.AddReview.as_view(), name="addreview"),
    path('like/<int:pk>/', views.like_view, name="list_commend"),
    # 127.0.0.1/domnfoironkwe_0394
    path('place/<str:place_id>/', views.place_info, name='place'),
    # 127.0.0.1/planner
    path('planner/', views.trip_planner, name='planner'),
    path('planner/gettime', views.get_travel_time, name='get_travel_time')
]

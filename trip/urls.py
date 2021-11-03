from django.urls import path
from . import views

app_name = 'trip'
urlpatterns = [
    path('', views.index, name='index'),
    path('tripplan/', views.HomeView.as_view(), name="tripplan"),
    path('tripdetail/<int:pk>/', views.DetailView.as_view(), name="tripdetail"),
    path('addpost/', views.AddPost.as_view(), name="addpost"),
    path('tripdetail/<int:pk>/addreview/', views.AddReview.as_view(), name="addreview"),
    path('like/<int:pk>/', views.likeview, name="list_commend"),
    # 127.0.0.1/domnfoironkwe_0394
    path('place/<str:place_id>/', views.place_info, name='place')

]

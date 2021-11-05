from django.urls import path
from . import views

app_name = 'trip'
urlpatterns = [
    path('', views.index, name='index'),
    path('tripplan/', views.AllTrip.as_view(), name="tripplan"),
    path('tripdetail/<int:pk>/', views.TripDetail.as_view(), name="tripdetail"),
    path('addpost/', views.AddPost.as_view(), name="addpost"),
    path('tripdetail/<int:pk>/addreview/', views.AddReview.as_view(), name="addreview"),
<<<<<<< HEAD
    path('like/<int:pk>/', views.likeview, name="list_commend"),
    path('tripdetail/edit/<int:pk>', views.EditPost.as_view(), name='editpost'),
=======
    path('like/<int:pk>/', views.like_view, name="list_commend"),
    path('tripdetail/edit/<int:pk>', views.EditPost.as_view(), name='editpost'),
    path('tripdetail/<int:pk>/remove', views.DeletePost.as_view(), name='deletepost'),
>>>>>>> a8e6967d8848a3133d3f45adf01873944b973982
    # 127.0.0.1/domnfoironkwe_0394
    path('place/<str:place_id>/', views.place_info, name='place')
]

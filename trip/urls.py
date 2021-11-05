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
    path('tripdetail/edit/<int:pk>', views.EditPost.as_view(), name='editpost'),
    path('tripdetail/<int:pk>/remove', views.DeletePost.as_view(), name='deletepost'),
    path('category/<str:cats>/', views.category, name='category'),
    path('addcategory/', views.AddCategory.as_view(), name="addcategory"),
    # 127.0.0.1/domnfoironkwe_0394
    path('place/<str:place_id>/', views.place_info, name='place')
]

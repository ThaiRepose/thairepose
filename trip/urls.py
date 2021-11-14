from django.urls import path
from . import views

app_name = 'trip'
urlpatterns = [
    path('', views.index, name='index'),
    path('tripplan/', views.AllTrip.as_view(), name="tripplan"),
    path('tripdetail/<int:pk>/', views.TripDetail.as_view(), name="tripdetail"),
    path('addpost/', views.AddPost.as_view(), name="addpost"),
    path('tripdetail/<int:pk>/addreview/', views.AddReview.as_view(), name="addreview"),
    path('likereview/', views.like_comment_view, name="like_comment"),
    path('dislikeview/', views.dislike_comment_view, name="dislike_comment"),
    path('likepost/<int:pk>/', views.like_post, name="list_trip"),
    path('tripdetail/edit/<int:pk>', views.EditPost.as_view(), name='editpost'),
    path('tripdetail/<int:pk>/remove', views.delete_post, name='deletepost'),
    path('category/<category>', views.CatsListView.as_view(), name='category'),
    # 127.0.0.1/domnfoironkwe_0394
    path('place/<str:place_id>/', views.place_info, name='place')
]

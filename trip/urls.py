from django.urls import path
from . import views

app_name = 'trip'
urlpatterns = [
    path('', views.index, name='index'),
    path('tripblog/', views.AllTrip.as_view(), name="tripplan"),
    path('likereview/', views.like_comment_view, name="like_comment"),
    path('tripdetail/<int:pk>/', views.trip_detail, name="tripdetail"),
    path('addpost/', views.add_post, name="addpost"),
    path('likepost/', views.like_post, name="like_trip"),
    path('tripdetail/edit/<int:pk>', views.EditPost.as_view(), name='editpost'),
    path('tripdetail/<int:pk>/remove', views.delete_post, name='deletepost'),
    path('category/<category>', views.CatsListView.as_view(), name='category'),
    # 127.0.0.1/domnfoironkwe_0394
    path('place/<str:place_id>/', views.place_info, name='place-detail')
]

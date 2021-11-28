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
    path('tripdetail/edit/<int:pk>', views.edit_post, name='editpost'),
    path('tripdetail/<int:pk>/remove', views.delete_post, name='deletepost'),
    path('category/<category>', views.CatsListView.as_view(), name='category'),
    path('addcomment/', views.post_comment, name="add_comment"),
    path('action/gettripqueries', views.get_trip_queries, name='get-trip-query'),
    # 127.0.0.1/domnfoironkwe_0394
    path('place/<str:place_id>/', views.place_info, name='place-detail'),
    path('place/<str:place_id>/like', views.place_like, name='place-like'),
    path('place/<str:place_id>/dislike', views.place_dislike, name='place-dislike'),
    path('place/<str:place_id>/addreview', views.place_review, name='place-review'),
    path('place/<str:place_id>/removereview', views.place_remove_review, name='place-remove-review'),
]

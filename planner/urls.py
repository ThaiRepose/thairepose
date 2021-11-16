from django.urls import path
from . import views

app_name = 'planner'
urlpatterns = [
    # 127.0.0.1/planner
    path('', views.planner_list, name='index'),
    # 127.0.0.1/planner/1/edit
    path('<int:planner_id>/edit', views.edit_planner, name='edit_plan'),
    path('<int:planner_id>/view', views.view_planner, name='view_plan'),
    path('action/create', views.create_planner, name='create'),
    path('action/delete/<int:planner_id>', views.delete_planner, name='delete'),
    path('action/edit', views.edit_planner_backend, name='post_edit'),
    path('gettime', views.get_travel_time, name='get_travel_time')
]
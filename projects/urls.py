from django.urls import path
from .views import *

app_name = 'projects'

urlpatterns = [
    path('<int:pk>/', ProjectDetailView.as_view(), name="main"),
    path('<int:pk>/management', BigtimeUpdate.as_view(), name="project_management"),
    path('long_desc/', update_long_descriptions, name="long_desc"),
    path('create_subs/', create_substitutions, name="create_subs"),
    path('add/', project_add, name="add"),
    path('templates/', export_template, name="templates"),
    path('galaxy_parse/', parse_galaxy, name="galaxy_parse"),
    path('create_comm_devs/', create_comm_devs, name="create_comm_devs"),
    path('add_bigtime_tasks/', add_bigtime_tasks, name="add_bigtime_tasks"),
    path('delete_bigtime_tasks/', delete_bigtime_tasks, name="delete_bigtime_tasks"),
]

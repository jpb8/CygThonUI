from django.urls import path
from .views import *

app_name = 'projects'

urlpatterns = [
    path('<int:pk>/', ProjectDetailView.as_view(), name="main"),
    path('long_desc/', update_long_descriptions, name="long_desc"),
    path('create_subs/', create_substitutions, name="create_subs"),
    path('add/', project_add, name="add"),
    path('templates/', export_template, name="templates"),
]

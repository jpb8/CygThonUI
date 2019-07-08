from django.urls import path
from .views import ProjectDetailView, update_long_descriptions, create_substitutions

app_name = 'projects'

urlpatterns = [
    path('<int:pk>/', ProjectDetailView.as_view(), name="main"),
    path('long_desc/', update_long_descriptions, name="long_desc"),
    path('create_subs/', create_substitutions, name="create_subs")
]
from django.urls import path
from .views import ProjectDetailView

app_name = 'projects'

urlpatterns = [
    path('<int:pk>/', ProjectDetailView.as_view(), name="main")
]
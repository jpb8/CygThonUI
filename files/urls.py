from django.urls import path
from .views import dds_upload

urlpatterns = [
    path('file_upload', dds_upload, name='file_upload')
]

from django.urls import path
from .views import dds_upload, file_print, DDSDetailView, export_dds

urlpatterns = [
    path('file_upload', dds_upload, name='file_upload'),
    path('dds', file_print, name='dds'),
    path('dds/<int:pk>/', DDSDetailView.as_view()),
    path('dds/export/', export_dds, name="dds_export"),
]

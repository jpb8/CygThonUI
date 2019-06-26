from django.urls import path
from .views import upload, file_print, DDSDetailView, export_dds, dds_upload, dtf_upload, dds_add_mapping,mapping_export

app_name = 'files'

urlpatterns = [
    path('upload', upload, name='upload'),
    path('dds_upload', dds_upload, name='dds_upload'),
    path('dtf_upload', dtf_upload, name='dtf_upload'),
    path('dds', file_print, name='dds'),
    path('dds/<int:pk>/', DDSDetailView.as_view()),
    path('dds/export/', export_dds, name="dds_export"),
    path('dds/dds_mappings_export/', mapping_export, name="dds_mappings_export"),
    path('dds/dds_add_mappings/', dds_add_mapping, name="dds_add_mappings"),
]

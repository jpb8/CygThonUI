from django.urls import path
from .views import *

app_name = 'files'

urlpatterns = [
    ## Files ##
    path('upload', upload, name='upload'),
    path('dds_upload', dds_upload, name='dds_upload'),
    path('dtf_upload', dtf_upload, name='dtf_upload'),
    ## DDS ##
    path('dds/<int:pk>/', DDSDetailView.as_view(), name="dds"),
    path('dds/export/', export_dds, name="dds_export"),
    path('dds/dds_mappings_export/', mapping_export, name="dds_mappings_export"),
    path('dds/export_cmds/', mapping_export_with_regs, name="export_cmds"),
    path('dds/dds_add_mappings/', dds_add_mapping, name="dds_add_mappings"),
    path('dds/correct_dec_check/', correct_device_check, name="correct_dec_check"),
    path('dds/unmapped_facs/', unmapped_facs, name="unmapped_facs"),
    path('dds/orphans/', find_orphans, name="orphans"),
    path('dds/fac_exist/', facs_dne, name="fac_exist"),
    path('dds/validate_commands/', validate_commands, name="validate_commands"),
    path('dds/get_mappings/', get_mappings, name="get_mappings"),
    path('dds/mapping_template/', mapping_template, name="mapping_template"),
    path('dds/delete/', dds_delete, name="dds_delete"),
    path('dds/validate_maps/', validate_mappings, name="validate_maps"),
    ## DTF ##
    path('dtf/<int:pk>/', DTFDetailView.as_view(), name="dtf"),
    path('dtf/export/', export_dtf, name='dtf_export'),
    path('dtf/unused_deids/', unmapped_dieds, name="unused_dieds"),
    path('dtf/delete/', dtf_delete, name="dtf_delete"),
    path('dtf/export_dtf_data/', export_dtf_data, name="export_dtf_data"),
    path('dtf/add_array/', add_array, name="add_array"),
]

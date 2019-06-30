from django.db import models
from django.utils import timezone
from django.conf import settings
from projects.models import Project
import pandas as pd

import os

from cygdevices.device import DeviceDef, UdcMap
from cygdevices.dtf import DTF as D


# Create your models here.
class DDS(models.Model):
    file = models.FileField(upload_to='dds/')
    uploaded = models.DateTimeField(auto_now=True)
    last_update = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.project, self.file)

    @property
    def base_file(self):
        return os.path.basename(str(self.file))

    @property
    def export_url(self):
        return "http://127.0.0.1:8000/files/dds/export/?id={}".format(self.pk)

    @property
    def xml(self):
        return DeviceDef(os.path.join(settings.MEDIA_ROOT, str(self.file)))

    def add_mappings(self, dtf_obj, excel):
        dtf_xml = dtf_obj.xml
        mappings = pd.read_excel(excel, sheet_name="Sheet1")
        error_log = self.xml.mapping_excel_import(mappings, dtf_xml)
        return error_log

    def check_facilities(self, excel):
        facs_df = pd.read_excel(excel, sheet_name="Sheet1")
        facs = facs_df["facility"].to_list()
        dne = self.xml.fac_exists_check(facs)
        return dne

    def save_document(self):
        self.xml.save()


class DTF(models.Model):
    file = models.FileField(upload_to="dtf/")
    uploaded = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.project, self.file)

    @property
    def xml(self):
        return D(os.path.join(settings.MEDIA_ROOT, str(self.file)))

    @property
    def base_file(self):
        return os.path.basename(str(self.file))

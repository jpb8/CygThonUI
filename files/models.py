from django.db import models
from django.conf import settings
from django.shortcuts import reverse

from projects.models import Project
import pandas as pd

import os

from cygdevices.device import DeviceDef
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
        return reverse("files:dds_export", kwargs={'id': self.pk})

    @property
    def xml(self):
        try:
            dds_xml = DeviceDef(self.file)
        except:
            print("DDS File not found at: {}".format(os.path.join(settings.MEDIA_URL, str(self.file))))
            return None
        return dds_xml

    def get_absolute_url(self):
        return reverse('files:dds', args=[str(self.pk)])

    def add_mappings(self, dtf_obj, excel, deid_only):
        dtf_xml = dtf_obj.xml
        dds_xml = self.xml
        if dtf_xml is not None and dds_xml is not None:
            mappings = pd.read_excel(excel, sheet_name="Sheet1")
            error_log = dds_xml.mapping_excel_import(mappings, dtf_xml, deid_only)
        else:
            error_log = ["DDS or DTF File not found"]
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
        try:
            dtf_xml = D(self.file)
        except:
            print("DTF File not found at: {}".format(os.path.join(settings.MEDIA_URL, str(self.file))))
            return None
        return dtf_xml

    @property
    def base_file(self):
        return os.path.basename(str(self.file))

    @property
    def export_url(self):
        return reverse("files:dtf_export", kwargs={'id': self.pk})

    def get_absolute_url(self):
        return reverse('files:dtf', args=[str(self.pk)])


class ScreenSubstitutions(models.Model):
    file = models.FileField(upload_to="dtf/")
    uploaded = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.project, self.file)

    @property
    def base_file(self):
        return os.path.basename(str(self.file))

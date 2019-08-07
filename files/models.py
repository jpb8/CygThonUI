from django.db import models
from django.conf import settings
from django.shortcuts import reverse

from projects.models import Project
import pandas as pd

import os

from cygdevices.device import DeviceDef
from cygdevices.dtf import DTF as D

from django.db.models.signals import pre_delete
from django.dispatch import receiver


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

    def check_facilities(self, excel, ):
        facs_df = pd.read_excel(excel, sheet_name="Sheet1")
        facs = facs_df["facility"].to_list()
        dne = self.xml.fac_exists_check(facs)
        return dne

    def validate_cmds(self, cmd_data, dtf):
        cmds = pd.read_excel(cmd_data, sheet_name="Sheet1")
        dds_xml = self.xml
        dtf_xml = dtf.xml
        errors = []
        for i, cmd in cmds.iterrows():
            pnt_type = cmd["pointtype"]
            reg = cmd["reg"].split(":")
            cmd_tag = "{}[{}]".format(reg[0], reg[1])
            if pnt_type == "manual entry":
                data = dds_xml.do_manual_entry_data(cmd["device"], cmd["command"], cmd["facility"])
                if data is not None:
                    tag = dtf_xml.deid_tagname(data["dg"], data["ld"])
                    if (
                            cmd_tag != tag or
                            int(cmd["value"]) != int(data["val"]) or
                            cmd["facility"] != data["fac"] or
                            cmd["udc"] != data["udc"]
                    ):
                        udc = str(cmd["udc"])
                        errors.append({
                            "device": cmd["device"],
                            "command": cmd["command"],
                            "fac": cmd["facility"],
                            "val": cmd["value"],
                            "dds_val": data["val"],
                            "udc": udc,
                            "dds_fac": data["udc"],
                            "reg": cmd_tag,
                            "dtf_reg": tag
                        })
            elif pnt_type == "telemetered":
                data = dds_xml.do_command_data(cmd["device"], cmd["command"], cmd["facility"])
                if data is not None:
                    tag = dtf_xml.deid_tagname(data["dg"], data["ld"])
                    if cmd_tag != tag or int(cmd["value"]) != int(data["val"]):
                        errors.append({
                            "device": cmd["device"],
                            "command": cmd["command"],
                            "fac": cmd["facility"],
                            "val": cmd["value"],
                            "dds_val": data["val"],
                            "udc": "None",
                            "dds_fac": "",
                            "reg": cmd_tag,
                            "dtf": tag
                        })
            else:
                data = "double"
        return errors

    def save_document(self):
        self.xml.save()


@receiver(pre_delete, sender=DDS)
def dds_pre_delete(sender, instance, **kwargs):
    instance.xml.delete()


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


@receiver(pre_delete, sender=DTF)
def dtf_pre_delete(sender, instance, **kwargs):
    instance.xml.delete()


class ScreenSubstitutions(models.Model):
    file = models.FileField(upload_to="dtf/")
    uploaded = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.project, self.file)

    @property
    def base_file(self):
        return os.path.basename(str(self.file))

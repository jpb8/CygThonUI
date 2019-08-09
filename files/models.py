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

    def _validator(self, cmd, data, pnt_type, manual, tag):
        """
        Runs a series of checks on command to validate
            1. cmd_tag != tag => tagName in DTF matches command
            2. int(cmd["value"]) != int(data["val"]) => value of command is DDS matching command (do only)
            3. cmd["facility"] != data["fac"] or cmd["udc"] != data["udc"] => Manual entry point matches (manual only)
        :param cmd: singled command pandas row
        :param data: data fetched form device and dtf
        :param pnt_type: point type (ao or do)
        :param manual: manual entry bool
        :param tag: tagName from DTF
        :return: True if valid, False if invalid
        """
        reg = cmd["reg"].split(":")
        cmd_tag = "{}[{}]".format(reg[0], reg[1])
        if cmd_tag != tag:
            return False, "Wrong Reg"
        if pnt_type == "do":
            if int(cmd["value"]) != int(data["val"]):
                return False, "Wrong Cmd Value"
        if manual:
            if cmd["facility"] != data["fac"] or cmd["udc"] != data["udc"]:
                return False, "Wrong manual Update Pnt"
        return True, None

    def validate_cmds(self, cmd_data, dtf):
        """
        Validates commands by:
            1. Fetching command from device
            2. Fetching where the command is pointed to in dtf
            3. Comparing fetched data to supplied command (see _validator method)
        :param cmd_data: pandas df object from commands excel import
        :param dtf: dtf object
        :return: List of invalid commands
        """
        cmds = pd.read_excel(cmd_data, sheet_name="Sheet1")
        dds_xml = self.xml
        dtf_xml = dtf.xml
        errors = []
        for i, cmd in cmds.iterrows():
            manual = True if cmd["pointtype"] == "manual entry" else False
            pnt_type = cmd["cmd_type"]
            data = dds_xml.cmd_data(cmd["device"], cmd["command"], cmd["facility"], pnt_type, manual)
            if data is not None:
                tag = dtf_xml.deid_tagname(data["dg"], data["ld"])
                valid, err = self._validator(cmd, data, pnt_type, manual, tag)
                if not valid:
                    udc = str(cmd["udc"])
                    errors.append({
                        "device": cmd["device"],
                        "command": cmd["command"],
                        "fac": cmd["facility"],
                        "val": cmd["value"],
                        "dds_val": data["val"],
                        "udc": udc,
                        "dds_fac": data["udc"] if "udc" in data else "NONE",
                        "reg": cmd["reg"],
                        "dtf_reg": tag,
                        "err_msg": err
                    })
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

from django.db import models
from django.utils import timezone
from django.conf import settings
from projects.models import Project

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
    def xml(self):
        return DeviceDef(os.path.join(settings.MEDIA_ROOT, self.file))

    def add_mappings(self, dtf_obj, excel):
        dtf_xml = dtf_obj.xml

        def dds_excel_import(mappings, dd, dtfxml):
            devices = mappings.device.unique()
            errs = []
            for d in devices:
                dev_points = mappings.loc[mappings['device'] == d]
                dev_arr = dev_points.array.unique()
                facs = []
                if dd.check_device(d) is not None:
                    for da in dev_arr:
                        arr_points = dev_points.loc[dev_points['array'] == da]
                        maps = []
                        for i, p in arr_points.iterrows():
                            udc, pnt_err = UdcMap.safe_create(dtfxml, p, da)
                            maps.append(udc) if udc is not None else errs.append(pnt_err)
                            facs.append(p["facilityid"]) if p["facilityid"] not in facs else None
                        map_log = dd.add_maps(d, da, maps)
                        fac_log = dd.add_facs(facs, d)
                        errs = errs + map_log + fac_log
                else:
                    errs.append("Device {} is not in XML".format(d))
            dd.save("docs/deviceDefinitions_20190530_updated.xml")


class DTF(models.Model):
    file = models.FileField(upload_to="dtf/")
    uploaded = models.DateTimeField(auto_now=True)
    last_update = models.DateTimeField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.project, self.file)

    @property
    def xml(self):
        return D(os.path.join(settings.MEDIA_ROOT, self.file))

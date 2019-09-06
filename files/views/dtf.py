from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import DetailView
from django.http import HttpResponse, Http404
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from files.models import DDS, DTF
from files.forms import DTFForm
from files.utils import build_ajax_response_dict

import os

import pandas as pd


def dtf_upload(request):
    if request.method == 'POST':
        form = DTFForm(request.POST, request.FILES)
        next = request.POST.get('next', '/')
        if form.is_valid():
            form.save()
        else:
            print("Error in form")
    return redirect(next)


def dtf_delete(request):
    dtf_id = request.GET.get("id")
    print(dtf_id)
    try:
        dtf = DTF.objects.get(pk=int(dtf_id))
    except ObjectDoesNotExist:
        return redirect("files:upload")
    dtf.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class DTFDetailView(DetailView):
    queryset = DTF.objects.all()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        proj = self.object.project
        data['ddss'] = DDS.objects.filter(project=proj)
        data['project'] = proj
        data["arrays"] = self.object.xml.all_arrays()
        return data


def export_dtf(request):
    dtf_id = request.GET.get("id")
    try:
        dtf = DTF.objects.get(pk=dtf_id)
        file_path = os.path.join(settings.MEDIA_ROOT, str(dtf.file))
        response = HttpResponse(dtf.xml.pretty_print(), content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
        response['X-Sendfile'] = file_path
    except:
        raise Http404
    return response


def unmapped_dieds(request):
    if request.method == "POST":
        dds_id = int(request.POST.get("dds-id"))
        dtf_id = int(request.POST.get("dtf-id"))
        try:
            dds = DDS.objects.get(pk=dds_id).xml
            dtf = DTF.objects.get(pk=dtf_id).xml
        except ObjectDoesNotExist:
            print("DTF or DDS not found")
            return redirect("files:upload")
        unused = dtf.unused_deids(dds)
        if request.is_ajax():
            data = build_ajax_response_dict(unused, "Unused ")
            return JsonResponse(data)
    return redirect("files:upload")


def import_dtf(request):
    dtf_id = request.POST.get("id")
    try:
        dtf = DTF.objects.get(pk=int(dtf_id)).xml
    except ObjectDoesNotExist:
        return redirect("files:upload")
    pnts = request.FILES["pnts"] if "pnts" in request.FILES else None
    if pnts:
        anologs = pd.read_excel(pnts, sheet_name="anolog")
        digitals = pd.read_excel(pnts, sheet_name="digital")
        devices = anologs.rtu.unique()
        for d in devices:
            array_type = "{}_A".format(d)
            array_nice_name = "{} Analog Points Array".format(d)
            arr = dtf.create_array(name=array_type, nice_name=array_nice_name)
            for pnt in anologs.loc[d['rtu'] == d]:
                index = pnt["anain.iospec.external"]
                bit = index.split()[-1]
                if len(bit) == 1:
                    deid = "00" + bit
                elif len(bit) == 2:
                    deid = "0" + bit
                else:
                    deid = bit
                dtf.create_ai_deid(array_type, deid, index, data_type=pnt["anain.type"])
        dtf.save()


def export_dtf_data(request):
    dtf_id = request.GET.get("id")
    try:
        dtf = DTF.objects.get(pk=int(dtf_id))
    except ObjectDoesNotExist:
        print("DTF or DDS not found")
        return redirect("files:upload")
    workbook = dtf.xml.create_array_excel()
    response = HttpResponse(workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename={}'.format("dtf_array_data.xlsx")
    return response

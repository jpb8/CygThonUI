from django.shortcuts import render, redirect
from django.http import JsonResponse

from projects.models import Project
from django.views.generic import DetailView
from django.http import HttpResponse, Http404, StreamingHttpResponse

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

from .models import DDS, DTF
from .forms import DDSForm, DTFForm
from .utils import build_ajax_response_dict

import os
from cygdevices.device import DeviceDef


def upload(request):
    cont_dict = {
        "dds_form": DDSForm,
        "dtf_form": DTFForm,
    }
    return render(request, 'files/file_upload.html', cont_dict)


def dds_upload(request):
    if request.method == 'POST':
        form = DDSForm(request.POST, request.FILES)
        next = request.POST.get('next', '/')
        if form.is_valid():
            form.save()
        else:
            print("Error in form")
    return redirect(next)


def dtf_upload(request):
    if request.method == 'POST':
        form = DTFForm(request.POST, request.FILES)
        next = request.POST.get('next', '/')
        if form.is_valid():
            form.save()
        else:
            print("Error in form")
    return redirect(next)


def file_print(request):
    p = Project.objects.get(pk=1)
    files = p.dds_set.all()
    file_strs = []
    code_string = ""
    for dds in files:
        device = DeviceDef("{}/{}".format("media", str(dds.file)))
        file_strs.append(device.all_unique_arrays())
    cont_dict = {
        "file_strs": file_strs,
        "code_string": code_string,
    }
    return render(request, 'files/dds.html', cont_dict)


class DDSDetailView(DetailView):
    queryset = DDS.objects.all()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['dtfs'] = DTF.objects.all()
        try:
            device = DeviceDef("{}/{}".format("media", str(self.object.file)))
            data['incorrect_dev'] = device.correct_dev_check()
            data['unmapped'] = device.mapped_fac_check()
        except:
            return data
        return data


def export_dds(request):
    dds_id = request.GET.get("id")
    dds = DDS.objects.get(pk=dds_id)
    file_path = os.path.join(settings.MEDIA_ROOT, str(dds.file))
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            response['X-Sendfile'] = file_path
            return response
    raise Http404


def dds_add_mapping(request):
    # Pass Excel file and dtf document to import script, return error logs
    if request.method == "POST":
        mappings = request.FILES["mappings"]
        deid_only = True if "deid-only" in request.POST else False
        try:
            dtf = DTF.objects.get(pk=int(request.POST.get("dtf-id")))
            dds = DDS.objects.get(pk=int(request.POST.get("dds-id")))
        except ObjectDoesNotExist:
            print("DTF or DDS not found")
            return redirect("files:upload")
        errors = dds.add_mappings(dtf, mappings, deid_only)
        if request.is_ajax():
            return JsonResponse({'errors': errors})
    return redirect("files:upload")


def mapping_export(request):
    dds_id = request.GET.get("id")
    try:
        dds = DDS.objects.get(pk=dds_id)
    except ObjectDoesNotExist:
        print("DTF or DDS not found")
        return redirect("files:upload")
    workbook = dds.xml.export_mappings()
    response = HttpResponse(workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename={}'.format("dds_mappings_export.xlsx")
    return response


@csrf_exempt
def correct_device_check(request):
    dds_id = request.POST.get("id")
    try:
        dds = DDS.objects.get(pk=dds_id)
    except ObjectDoesNotExist:
        print("DTF or DDS not found")
        return redirect("files:upload")
    non_matches = dds.xml.correct_dev_check()
    if request.is_ajax():
        data = build_ajax_response_dict(non_matches, "Wrong Device")
        return JsonResponse(data)
    return redirect("files:upload")


@csrf_exempt
def unmapped_facs(request):
    if request.method == "POST":
        dds_xml = DDS.objects.get(pk=int(request.POST.get("id"))).xml
        map_facs = request.POST.get("map")
        unmapped = dds_xml.mapped_fac_check()
        if map_facs:
            log = []
            for f in unmapped:
                outcome = dds_xml.add_facility(f["facility"], f["device"])
                log.append({"outcome": outcome})
            data = build_ajax_response_dict(log, "Facility Added Outcomes")
            dds_xml.save()
            return JsonResponse(data)
        else:
            data = build_ajax_response_dict(unmapped, "Unmapped Facilities")
            return JsonResponse(data)
    if request.method == "GET":
        dds_id = request.GET.get("id")
        try:
            dds = DDS.objects.get(pk=dds_id)
        except ObjectDoesNotExist:
            print("DTF or DDS not found")
            return redirect("files:upload")
        unmapped = dds.xml.mapped_fac_check()
        if request.is_ajax():
            data = build_ajax_response_dict(unmapped, "Unmapped Facilities")
            return JsonResponse(data)
    return redirect("files:upload")


def find_orphans(request):
    if request.method == "POST":
        try:
            dtf = DTF.objects.get(pk=int(request.POST.get("dtf-id")))
            dds = DDS.objects.get(pk=int(request.POST.get("dds-id")))
        except ObjectDoesNotExist:
            print("DTF or DDS not found")
            return redirect("files:upload")
        orphans = dds.xml.find_orphans(dtf.xml)
        if request.is_ajax():
            if request.is_ajax():
                data = build_ajax_response_dict(orphans, "Orphans")
                return JsonResponse(data)
    return redirect("files:upload")


def facs_dne(request):
    if request.method == "POST":
        try:
            dds = DDS.objects.get(pk=int(request.POST.get("dds-id")))
            facs = request.FILES["facs"]
        except ObjectDoesNotExist:
            print("DTF or DDS not found")
            return redirect("files:upload")
        dne = dds.check_facilities(facs)
        if request.is_ajax():
            data = build_ajax_response_dict(dne, "Non Existent Facs")
            return JsonResponse(data)
    return redirect("files:upload")

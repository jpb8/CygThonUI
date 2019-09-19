from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.views.generic import DetailView
from django.http import HttpResponse, Http404
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

from files.models import DDS, DTF
from files.forms import DDSForm, DTFForm
from files.utils import build_ajax_response_dict

import os


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


def dds_delete(request):
    dds_id = request.GET.get("id")
    try:
        dds = DDS.objects.get(pk=int(dds_id))
    except ObjectDoesNotExist:
        return redirect("files:upload")
    dds.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class DDSDetailView(DetailView):
    queryset = DDS.objects.all()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        proj = self.object.project
        data['dtfs'] = DTF.objects.filter(project=proj)
        data['project'] = proj
        try:
            data['devices'] = self.object.xml.all_devices()
        except:
            return data
        return data


def export_dds(request):
    dds_id = request.GET.get("id")
    try:
        dds = DDS.objects.get(pk=dds_id)
        file_path = os.path.join(settings.MEDIA_ROOT, str(dds.file))
        response = HttpResponse(dds.xml.pretty_print(), content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
        response['X-Sendfile'] = file_path
    except:
        raise Http404
    return response


def dds_add_mapping(request):
    # Pass Excel file and dtf document to import script, return error logs
    if request.method == "POST":
        mappings = request.FILES["mappings"]
        deid_only = True if "deid-only" in request.POST else False
        add_dgs = True if "add-dgs" in request.POST else False
        try:
            dtf = DTF.objects.get(pk=int(request.POST.get("dtf-id")))
            dds = DDS.objects.get(pk=int(request.POST.get("dds-id")))
        except ObjectDoesNotExist:
            print("DTF or DDS not found")
            return redirect("files:upload")
        # try:
        errors = dds.add_mappings(dtf, mappings, deid_only, add_dgs)
        # except:
        #     errors = ["Error Handling Excel File. Please use template file", ]
        if request.is_ajax():
            errs = []
            for e in errors:
                errs.append({"Log": e})
            data = build_ajax_response_dict(errs, "Import Log")
            devices = dds.xml.all_devices()
            devices_html = render_to_string("files/snippets/device_accord.html", {"devices": devices})
            data["devices_html"] = devices_html
            return JsonResponse(data)
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


def mapping_export_with_regs(request):
    dds_id = request.POST.get("dds-id")
    dtf_id = request.POST.get("dtf-id")
    try:
        dds = DDS.objects.get(pk=int(dds_id))
        dtf = DTF.objects.get(pk=int(dtf_id))
    except ObjectDoesNotExist:
        print("DTF or DDS not found")
        return redirect("files:upload")
    workbook = dds.xml.export_mappings(dtf.xml)
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
            devices = dds_xml.all_devices()
            dds_xml.save()
            devices_html = render_to_string("files/snippets/device_accord.html", {"devices": devices})
            data["devices_html"] = devices_html
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
            dtf = DTF.objects.get(pk=int(request.POST.get("dtf-id"))).xml
            dds = DDS.objects.get(pk=int(request.POST.get("dds-id"))).xml
        except ObjectDoesNotExist:
            print("DTF or DDS not found")
            return redirect("files:upload")
        if dtf is not None and dds is not None:
            orphans = dds.find_orphans(dtf)
        else:
            orphans = [{"ERROR": "DDS or DTF file not found"}]
        if request.is_ajax():
            if request.is_ajax():
                data = build_ajax_response_dict(orphans, "Orphans")
                return JsonResponse(data)
    return redirect("files:upload")


def facs_dne(request):
    if request.method == "POST":
        if "facs" not in request.FILES:
            return JsonResponse({"error": True})
        facs = request.FILES["facs"] if "facs" in request.FILES else None
        try:
            dds = DDS.objects.get(pk=int(request.POST.get("dds-id")))
        except ObjectDoesNotExist:
            print("DTF or DDS not found")
            return redirect("files:upload")
        dne = dds.check_facilities(facs)
        if request.is_ajax():
            data = build_ajax_response_dict(dne, "Non Existent Facs")
            return JsonResponse(data)
    return redirect("files:upload")


def validate_commands(request):
    if request.method == "POST":
        if "cmds" not in request.FILES:
            return JsonResponse({"error": True})
        cmd_data = request.FILES["cmds"] if "cmds" in request.FILES else None
        try:
            dds = DDS.objects.get(pk=int(request.POST.get("dds-id")))
            dtf = DTF.objects.get(pk=int(request.POST.get("dtf-id")))
        except ObjectDoesNotExist:
            print("DTF or DDS not found")
            return redirect("files:upload")
        errors = dds.validate_cmds(cmd_data, dtf)
        if request.is_ajax():
            data = build_ajax_response_dict(errors, "Command Errors")
            return JsonResponse(data)
    return redirect("files:upload")


@csrf_exempt
def get_mappings(request):
    if request.method == "POST":
        data_group = request.POST.get("data_group")
        device = request.POST.get("device")
        try:
            dds = DDS.objects.get(pk=int(request.POST.get("id"))).xml
        except ObjectDoesNotExist:
            print("DTF or DDS not found")
            return redirect("files:upload")
        maps = dds.all_mappings(device, data_group)
        if request.is_ajax():
            data = build_ajax_response_dict(maps, "All Mappings")
            return JsonResponse(data)
    return redirect("home")


def validate_mappings(request):
    if request.method == "POST":
        if "pnts" not in request.FILES:
            return JsonResponse({"error": True})
        pnt_data = request.FILES["pnts"]
        try:
            dds = DDS.objects.get(pk=int(request.POST.get("dds-id")))
            dtf = DTF.objects.get(pk=int(request.POST.get("dtf-id"))).xml
        except ObjectDoesNotExist:
            print("DTF or DDS not found")
            return redirect("files:upload")
        errors = dds.validate_mappings(dtf, pnt_data)
        if request.is_ajax():
            data = build_ajax_response_dict(errors, "Mapping Errors")
            return JsonResponse(data)
    return redirect("files:upload")




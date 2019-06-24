from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import DDSForm, DTFForm
from projects.models import Project
from django.views.generic import DetailView
from django.http import HttpResponse, Http404
from .models import DDS, DTF
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

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
        if form.is_valid():
            form.save()
        else:
            print("Error in form")
    return redirect('files:upload')


def dtf_upload(request):
    if request.method == 'POST':
        form = DTFForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        else:
            print("Error in form")
    return redirect('files:upload')


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
        device = DeviceDef("{}/{}".format("media", str(self.object.file)))
        data['incorrect_dev'] = device.correct_dev_check()
        data['unmapped'] = device.mapped_fac_check()
        data['dtfs'] = DTF.objects.all()
        return data


def export_dds(request):
    dds_id = request.POST.get("id")
    dds = DDS.objects.get(pk=dds_id)
    file_path = os.path.join(settings.MEDIA_ROOT, dds.file)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read())
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


def dds_add_mapping(request):
    # Pass Excel file and dtf document to import script, return error logs
    if request.method == "POST":
        mappings = request.FILES["mappings"]
        try:
            dtf = DTF.objects.get(pk=int(request.POST.get("dtf-id")))
            dds = DDS.objects.get(pk=int(request.POST.get("dds-id")))
            errors = dds.add_mappings(dtf, mappings)
        except ObjectDoesNotExist:
            print("DTF or DDS not found")
    return redirect("files:upload")

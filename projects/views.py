from django.views.generic import DetailView
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from .models import Project
from .forms import ProjectForm

from files.forms import DDSForm, DTFForm

from cygdevices.substitutions import Substitutions
from cygdevices.points import Points


def index(request):
    cont_dict = {
        "projects": Project.objects.all(),
        "form": ProjectForm
    }
    return render(request, 'index.html', cont_dict)


def project_add(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            print("Error in Form")
    return redirect("home")


class ProjectDetailView(DetailView):
    queryset = Project.objects.all()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['dds_form'] = DDSForm(initial={"project": self.object.pk})
        data['dtf_form'] = DTFForm(initial={"project": self.object.pk})
        return data


def update_long_descriptions(reqeust):
    if reqeust.method == "POST":
        if "points" not in reqeust.FILES:
            return JsonResponse({"error": True})
        pnts = Points(reqeust.FILES.get("points"), sheet="Sheet1")
        file_name = reqeust.FILES["points"].name
        pnts.update_point_desc()
        workbook = pnts.export()
        response = HttpResponse(workbook,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename={}_updated.xlsx'.format(file_name.split(".")[0])
        return response
    return redirect("home")


def create_substitutions(request):
    if request.method == "POST":
        file = request.FILES.get("subs")
        name = file.name.split(".")[0]
        s = Substitutions(file)
        s.build_rules()
        response = HttpResponse(s.pretty_print(), content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename={}.xml'.format(name)
        response['X-Sendfile'] = "{}.xml".format(name)
        return response
    return redirect("home")


def export_template(request):
    file_type = request.GET.get("file") if 'file' in request.GET else None
    if file_type is not None:
        if file_type == "subs":
            workbook = Substitutions.template()
            response = HttpResponse(workbook,
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=Excel2XML_substitions_template.xlsx'
            return response
    return redirect("home")

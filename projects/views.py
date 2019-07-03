from django.views.generic import DetailView
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from .models import Project
from files.forms import DDSForm, DTFForm

from cygdevices.points import Points


def index(request):
    cont_dict = {
        "projects": Project.objects.all()
    }
    return render(request, 'index.html', cont_dict)


class ProjectDetailView(DetailView):
    queryset = Project.objects.all()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['dds_form'] = DDSForm
        data['dtf_form'] = DTFForm
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
        response['Content-Disposition'] = 'attachment; filename={}'.format(
            "{}_Updated.xlsx".format(file_name.split(".")[0])
        )
        return response
    return redirect("home")

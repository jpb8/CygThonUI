from django.views.generic import DetailView
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.utils.encoding import codecs

from .models import Project
from .forms import ProjectForm

from files.forms import DDSForm, DTFForm

from cygdevices.substitutions import Substitutions
from cygdevices.points import Points
from cygdevices.galaxy import transform_galaxy
from cygdevices.commdev import MasterComm
from projman import DevopsData, BigTime
from projman.devops.utils import parse_tiga_id
from cygnet.settings import DEVOPS_TOKEN, BIGTIME_TOKEN, BIGTIME_FIRM_KEY


@login_required()
def index(request):
    cont_dict = {
        "projects": request.user.project_set.all(),
        "form": ProjectForm
    }
    return render(request, 'index.html', cont_dict)


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('home'))
            else:
                return HttpResponse("ACCOUNT NOT ACTIVE")
        else:
            print('Someone tried to login and failed')
            print('User: {} and password: {}'.format(username, password))
            return HttpResponse("invalid login details")
    return render(request, 'login.html')


@login_required()
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


@login_required()
def project_add(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            proj = form.save()
            proj.members.add(request.user)
        else:
            print("Error in Form")
    return redirect("home")


class ProjectDetailView(DetailView):
    queryset = Project.objects.all()

    def get_object(self, queryset=None):
        obj = super(ProjectDetailView, self).get_object(queryset=queryset)
        if self.request.user not in obj.members.all():
            raise Http404()
        return obj

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


def parse_galaxy(request):
    if request.method == "POST":
        file = request.FILES.get("galaxy")
        parse_type = request.POST.get("parseType")
        name = file.name.split(".")[0]
        new_galaxy = transform_galaxy(file, parse_type)
        response = HttpResponse(new_galaxy,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename={}.xlsx'.format(name)
        response['X-Sendfile'] = "{}.xlsx".format(name)
        return response
    return redirect("home")


def create_comm_devs(request):
    if request.method == "POST":
        file = request.FILES.get("commdevs")
        name = file.name.split(".")[0]
        mast_comm = MasterComm()
        mast_comm.import_devs(file)
        response = HttpResponse(mast_comm.pretty_print(), content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename={}.xml'.format(name)
        response['X-Sendfile'] = "{}.xml".format(name)
        return response
    return redirect("home")


def export_template(request):
    file_type = request.GET.get("file") if 'file' in request.GET else None
    if file_type is not None:
        if file_type == "subs":
            workbook = Substitutions.template()
            name = "Excel2XML_substitions_template.xlsx"
        elif file_type == "commdevs":
            workbook = MasterComm.template()
            name = "comm_dev_import_template.xlsx"
        else:
            return redirect("home")  # Go back to same location??
        response = HttpResponse(workbook,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename={}'.format(name)
        return response
    return redirect("home")


class BigtimeUpdate(DetailView):
    queryset = Project.objects.all()
    template_name = 'projects/management.html'

    def get_object(self, queryset=None):
        obj = super(BigtimeUpdate, self).get_object(queryset=queryset)
        if self.request.user not in obj.members.all():
            raise Http404()
        return obj

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.object.devops_name:
            sync_data = self.object.bigtime_devops_sync()
            data['task_breakdown'] = sync_data["task_breakdown"]
            data['bigtime_tasks'] = sync_data["bigtime_tasks"]
            data['bigtime_id'] = sync_data["bigtime_id"]
        return data


def add_bigtime_tasks(request):
    if request.method == "POST":
        bigtime_id = request.POST.get("bigtime_id")
        bigtime_api = BigTime(access_token=BIGTIME_TOKEN, firm_key=BIGTIME_FIRM_KEY)
        tasks = []
        for task, name in request.POST.items():
            if task.startswith("task"):
                service_disc = task.split("_")[-1]
                tasks.append({"task_name": name, "service_disc": service_disc})
        bigtime_api.create_tasks(bigtime_id, tasks)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

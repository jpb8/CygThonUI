from django.utils import timezone
from django.views.generic import DetailView
from .models import Project
from files.forms import DDSForm, DTFForm


class ProjectDetailView(DetailView):
    queryset = Project.objects.all()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['dds_form'] = DDSForm
        data['dtf_form'] = DTFForm
        return data
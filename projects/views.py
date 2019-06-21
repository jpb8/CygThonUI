from django.utils import timezone
from django.views.generic import DetailView
from .models import Project


class ProjectDetailView(DetailView):
    queryset = Project.objects.all()

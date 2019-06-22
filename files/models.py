from django.db import models
from django.utils import timezone
from projects.models import Project


# Create your models here.
class DDS(models.Model):
    file = models.FileField(upload_to='dds/')
    uploaded = models.DateTimeField(auto_now=True)
    last_update = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.project, self.file)


class DTF(models.Model):
    file = models.FileField(upload_to="dtf/")
    uploaded = models.DateTimeField(auto_now=True)
    last_update = models.DateTimeField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.project, self.file)

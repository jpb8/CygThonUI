from django.db import models
from django.utils import timezone
from projects.models import Projects


# Create your models here.
class DDS(models.Model):
    file = models.FileField(upload_to="dds/")
    uploaded = models.DateTimeField(auto_now=True)
    last_update = models.DateTimeField()
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.last_update = timezone.now()


class DTF(models.Model):
    file = models.FileField(upload_to="dtf/")
    uploaded = models.DateTimeField(auto_now=True)
    last_update = models.DateTimeField()
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.last_update = timezone.now()

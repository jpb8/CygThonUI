from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=124)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('projects:main', args=[str(self.id)])

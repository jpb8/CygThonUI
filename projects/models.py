from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=124)
    members = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('projects:main', args=[str(self.id)])

    def check_user(self, user):
        if user in self.members:
            return True
        else:
            return False

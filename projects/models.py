from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Projects(models.Model):
    name = models.CharField(max_length=124)
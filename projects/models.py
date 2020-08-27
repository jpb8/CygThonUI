from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User

from projman import DevopsData, BigTime
from projman.devops.utils import parse_tiga_id
from cygnet.settings import DEVOPS_TOKEN, BIGTIME_TOKEN, BIGTIME_FIRM_KEY

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=124)
    devops_name = models.CharField(max_length=124, null=True)
    tiga_id = models.CharField(max_length=10, null=True)
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

    def bigtime_devops_sync(self):
        devops_api = DevopsData(DEVOPS_TOKEN)
        bigtime_api = BigTime(BIGTIME_TOKEN, BIGTIME_FIRM_KEY)
        project_features = devops_api.project_features(self.devops_name)
        task_breakdown = devops_api.get_task_with_service_disciplines(self.devops_name,
                                                                      parse_tiga_id(self.devops_name),
                                                                      project_features)
        bigtime_tasks, bigtime_id = bigtime_api.task_breakdown_from_tiga_id(parse_tiga_id(self.devops_name))
        for service, tasks in task_breakdown.items():
            if service in bigtime_tasks:
                for task in tasks:
                    task["in_bigtime"] = True if task["task_id"] in bigtime_tasks[service]["ids"] else False
            else:
                for task in tasks:
                    task["in_bigtime"] = False
        return {"task_breakdown": task_breakdown, "bigtime_tasks": bigtime_tasks, "bigtime_id": bigtime_id}

import requests
from .utils import *


class BigTime:
    def __init__(self, access_token, firm_key):
        self.access_token = access_token
        self.firm_key = firm_key
        self.base_url = "https://iq.bigtime.net/BigtimeData/api/v2/"
        self.headers = {"X-Auth-Token": self.access_token, "X-Auth-Realm": self.firm_key}

    def project_task_breakdown(self, proj_id):
        task_url = "{}task/listByProject/{}?showCompleted=True".format(self.base_url, str(proj_id))
        response = requests.get(task_url, headers=self.headers)
        parsed_response = response.json()
        task_obj = create_task_object(parsed_response)
        return task_obj

    def bigtime_projects(self):
        project_picklist_url = "{}picklist/projects".format(self.base_url)
        all_projects = requests.get(project_picklist_url, headers=self.headers)
        all_projects = all_projects.json()
        return build_project_dict(all_projects)

    def project_search_from_tiga_id(self, tiga_id):
        all_projects = self.bigtime_projects()
        if tiga_id in all_projects:
            return all_projects[tiga_id]
        else:
            return False

    def task_breakdown_from_tiga_id(self, tiga_id):
        project_id = self.project_search_from_tiga_id(tiga_id)
        if not project_id:
            return False
        return self.project_task_breakdown(project_id)

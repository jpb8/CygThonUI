from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from .utils import *


class DevopsData:
    def __init__(self, access_token):
        self.access_token = access_token
        self.org_url = "https://dev.azure.com/tiga"
        self.connection = None
        self._establish_connection()

    def _establish_connection(self):
        credentials = BasicAuthentication('', self.access_token)
        self.connection = Connection(base_url=self.org_url, creds=credentials)

    def all_projects(self):
        """
        :return: All projects for listed DevOps Access token
        """
        core_client = self.connection.clients.get_core_client()
        return core_client.get_projects()

    def project_features(self, project_id):
        """
        :param project_id: DevOps Project Id or Name
        :return: Dicts of Project Dicts containing tiga_id and there tasks
                Ex: {project_id: {tiga_id: str, tasks: []}, . . }
        """
        search_request = {"$orderBy": None, "$skip": 0, "$top": 100,
                          "filters": {"System.WorkItemType": ["Feature"]},
                          "includeFacets": True, "searchText": "Feature"}
        search_client = self.connection.clients_v6_0.get_search_client()
        features = []
        try:
            for work_item in search_client.fetch_work_item_search_results(search_request, project=project_id).results:
                fields = work_item.fields
                if fields["system.workitemtype"] == "Feature":
                    features.append(fields["system.id"])
        except:
            print("Project: {}".format(project_id))
        return features

    def features_for_project_list(self, project_list):
        """
        :param project_list: list of project objects
        :return: Dicts of Project Dicts containing tiga_id and there tasks
                Ex: {project_id: {tiga_id: str, tasks: []}, . . }
        """
        search_request = {"$orderBy": None, "$skip": 0, "$top": 100,
                          "filters": {"System.WorkItemType": ["Feature"]},
                          "includeFacets": True, "searchText": "Feature"}
        search_client = self.connection.clients_v6_0.get_search_client()
        project_data = {}
        for p in project_list:
            project_data[p.id] = {"tiga_id": parse_tiga_id(p.name), "tasks": []}
            for epic in search_client.fetch_work_item_search_results(search_request, project=p.id).results:
                fields = epic.fields
                if fields["system.workitemtype"] == "Feature":
                    project_data[p.id]["tasks"].append(fields["system.id"])
        return project_data

    def get_task_with_service_disciplines(self, proj_id, proj_tiga_id, task_ids):
        """
        Gets data for supplied tasks with Custom.ServiceDisciplines column attached
        :param proj_id: DevOps Project ID
        :param proj_tiga_id: TIGA Project ID
        :param task_ids: List of DevOps WorkItem Ids
        :return:
        """
        wi_request = {
            "ids": task_ids,
            "fields": ["System.Id", "System.Title", "System.WorkItemType", "Custom.ServiceDisciplines"]
        }
        work_item_client = self.connection.clients.get_work_item_tracking_client()

        classified_project = {}
        try:
            classificaitons = work_item_client.get_work_items_batch(project=proj_id, work_item_get_request=wi_request)
        except:
            return classified_project
        for c in classificaitons:
            wid, serv_disc, feat_name = get_feature_id_and_sevice_disc(c)
            if not serv_disc:
                continue
            if serv_disc in classified_project:
                classified_project[serv_disc].append({"task_id": wid, "task_name": feat_name})
            else:
                classified_project[serv_disc] = [{"task_id": wid, "task_name": feat_name}, ]
        return classified_project


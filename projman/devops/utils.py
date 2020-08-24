def retrieve_task_name(title):
    return title.split(": ")[-1]


def parse_tiga_id(proj_name):
    if proj_name[3] == "-" and proj_name[6] == "-":
        return proj_name[:10]
    else:
        return proj_name.split(" ")[0]


def get_feature_id_and_sevice_disc(work_item):
    fields = work_item.fields
    wid = int(fields["System.Id"])
    serv_disc = fields["Custom.ServiceDisciplines"] if "Custom.ServiceDisciplines" in fields else None
    feature_name = "Feature {}: {}".format(wid, fields["System.Title"])
    return wid, serv_disc, feature_name

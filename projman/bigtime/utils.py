def pull_devops_id_from_task(task):
    if task["TaskNm"].startswith("Feature"):
        name = int(task["TaskNm"].split(":")[0].split(" ")[-1])
    else:
        name = False
    return name


def create_task_object(data):
    task_object = {}
    for task in data:
        devops_id = pull_devops_id_from_task(task)
        if not task["TaskGroup"] or not devops_id:
            continue
        if task["TaskGroup"] not in task_object:
            task_object[task["TaskGroup"]] = [devops_id,]
        else:
            task_object[task["TaskGroup"]].append(devops_id)
    return task_object


def parse_proj_name(name):
    if "," not in name:
        return False
    else:
        return name.split(",")[0]


def build_project_dict(proj_data):
    data = {}
    for proj in proj_data:
        pasred_name = parse_proj_name(proj["Name"])
        if pasred_name:
            data[pasred_name] = proj["Id"]
    return data
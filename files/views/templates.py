from cygdevices.device import DeviceDef
from django.http import HttpResponse


def mapping_template(reqeust):
    workbook = DeviceDef.mappings_template()
    response = HttpResponse(workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename={}'.format("Mappings_import_template.xlsx")
    return response

def command_validation_template(request):
    #TODO
    pass

def mapping_validation_template(request):
    #TODO
    pass

from cygdevices.device import DeviceDef
from django.http import HttpResponse
from cygdevices.xml import XmlFile


def build_http_response(workbook, name):
    response = HttpResponse(workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename={}'.format(name)
    return response


def mapping_template(reqeust):
    workbook = DeviceDef.mappings_template()
    response = HttpResponse(workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename={}'.format("Mappings_import_template.xlsx")
    return response


def command_validation_template(request):
    sheet = {
        "cmd_type": ["ao", "do", "do"],
        "pointtype": ["telemetered", "telemetered", "manual entry"],
        "reg": ["AO_N45:9", "DO_N44:1", "DO_N44:1"],
        "value": ["0", "1", "2"],
        "facility": ["ANDW_PUMP5", "ANDW_A_PSTATION", "ANDW_A_PSTATION"],
        "udc": ["FSP", "", "ESDRS"],
        "command": ["FSP", "ESD", "ESDRS"],
        "device": ["ANDW_DEV", "ANDW_DEV", "ANDW_DEV"]
    }
    sheets = [sheet, ]
    workbook = XmlFile.template_export(sheets)
    response = build_http_response(workbook, "command_validation_template.xlsx")
    return response


def mapping_validation_template(request):
    sheet = {
        "point": ["EAGL_A_VSTATION_TEMP", "MID2_VALVE27_DISABLE", "EBE2_VALVE34_VSTATUS"],
        "register": ["AI_MT_TK_N4X:52", "DI_N40:15", "DI_N40:5"],
        "bit": ["0", "30", "26"],
        "bit2": ["0", "0", "27"]
    }
    sheets = [sheet, ]
    workbook = XmlFile.template_export(sheets)
    response = HttpResponse(workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename={}'.format("mapping_validation_template.xlsx")
    return response


def command_import_template(request):
    sheet = {
        "device": ["HAY2_DEV", "KLLR_DEV", "KLLR_DEV"],
        "facility": ["HAY2_D_RUN1", "KLLR_A_PSTATION", "KLLR_A_PSTATION"],
        "name": ["FSP", "RESET", "RESET"],
        "description": ["Flow Setpoint", "Station Reset", "Station Reset"],
        "comp_type": ["DG_T_DEV", "DG_T_DEV", "CYUPDTPT"],
        "data_group": ["CMD_N453", "CMD_N4413", ""],
        "value": ["", "1", ""],
        "update_fac": ["", "", "KLLR_A_PSTATION"],
        "udc": ["", "", "RESET"],
        "site": ["", "", "CRD1"],
        "service": ["", "", "UIS"],
        "utype": ["", "", "1"]
    }
    sheets = [sheet, ]
    workbook = XmlFile.template_export(sheets)
    response = HttpResponse(workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename={}'.format("command_import_template.xlsx")
    return response


def dtf_data_group_import(request):
    sheet = {
        "data_group": ["DG1", "DG2", "DG2"],
        "reg_num": ["44006", "44002", "44003"],
        "bit": ["", "", "1"],
        "description": ["Test Desc 1", "Test Desc 2", "Test Desc 3"],
        "udc": ["TESTPSI", "TESTDENS", ""],
        "dtype": ["i2", "ui2", "boolean"]
    }
    sheets = [sheet, ]
    workbook = XmlFile.template_export(sheets)
    response = HttpResponse(workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename={}'.format("dtf_dg_import_template.xlsx")
    return response

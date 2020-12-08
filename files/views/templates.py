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


def facility_import_template(request):
    sheet = {
        "device": ["TEST_DEV", "TEST2_DEV", "TEST2_DEV"],
        "facility": ["TEST_FAC_ONE", "TEST2_FAC_ONE", "TEST2_FAC_TWO"],
        "ordinal": ["1", "20", "40"]
    }
    sheets = [sheet, ]
    workbook = XmlFile.template_export(sheets)
    response = build_http_response(workbook, "facility_import_template.xlsx")
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
        "reg_number": ["43000", "43001", ""],
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
        "nice_name": ["Nice Name 1", "Nice Name 2", "Nice Name 2"],
        "deid": ["DEID1", "DEID1", "DEID2"],
        "tagname": ["DeviceTag[0]", "DeviceTag[1]", "DeviceTag[2]"],
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


def dtf_data_group_modbus_import(request):
    sheet = {
        "data_group": ["DG1", "DG2", "DG2"],
        "nice_name": ["Nice Name 1", "Nice Name 2", "Nice Name 2"],
        "deid": ["DEID1", "DEID1", "DEID2"],
        "reg_num": ["44006", "44002", "101"],
        "bit": ["", "", "1"],
        "description": ["Test Desc 1", "Test Desc 2", "Test Desc 3"],
        "udc": ["TESTPSI", "TESTDENS", ""],
        "dtype": ["i2", "ui4", "boolean"],
        "offset": ["-40001", "-40001", "-1"],
        "func_code": ["3", "3", "1"],
        "reg_byte_len": ["2", "4", "2"],
    }
    sheets = [sheet, ]
    workbook = XmlFile.template_export(sheets)
    response = HttpResponse(workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename={}'.format("dtf_dg_modbus_import_template.xlsx")
    return response

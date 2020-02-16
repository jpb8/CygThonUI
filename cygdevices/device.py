from lxml import etree
from lxml.etree import SubElement
import pandas as pd
from io import BytesIO, StringIO
import os
import math

from .xml import XmlFile


class DeviceDef(XmlFile):

    def check_device(self, device_id):
        """
        Check to see of the device exists in the xml by looking for the device_id attr in the device elements
        :param device_id:
        :return: True if exists, False if Not
        """
        return True if self.xml.find('./Device[@device_id="{}"]'.format(device_id)) is not None else None

    def get_device(self, device_id):
        """
        Gets device element
        :param device_id: Name of the device in CygNet
        :return: ETREE element for that device
        """
        return self.xml.find('./Device[@device_id="{}"]'.format(device_id))

    def device_dgs_element(self, device_id):
        return self.get_device(device_id).find("DataGroups") if self.get_device(device_id) is not None else None

    def device_facs_element(self, device_id):
        return self.get_device(device_id).find("FacilityLinks") if self.get_device(device_id) is not None else None

    def device_uis_element(self, device_id):
        return self.get_device(device_id).find("UisCommands") if self.get_device(device_id) is not None else None

    def find_command(self, device, cmd_name, fac):
        if self.device_uis_element(device) is None:
            return None
        return self.device_uis_element(device).find(
            "./UisCommand/CommandAttributes/[Name='{}'][Facility='{}']/..".format(cmd_name, fac))

    def find_command_component(self, device, cmd_name, fac, component):
        if self.find_command(device, cmd_name, fac) is None:
            return None
        command = self.find_command(device, cmd_name, fac)
        return command.find("CommandComponents/Component[@type='{}']".format(component))

    def do_command_data(self, device, cmd_name, fac):
        cmd_comp = self.find_command_component(device, cmd_name, fac, "DG_T_DEV")
        if cmd_comp is None:
            return None
        data = dict()
        data["dg"] = cmd_comp.find("Param[@key='DGTYPE']").get("value")
        if len(cmd_comp.xpath("Param[starts-with(@key,'L')]")) == 0:
            data["ld"] = None
            data["val"] = None
        else:
            xpath = cmd_comp.xpath("Param[starts-with(@key,'L')]")[0]
            data["ld"] = xpath.get("key")
            data["val"] = xpath.get("value")
        return data

    def ao_command_data(self, device, cmd_name, fac):
        cmd_comp = self.find_command_component(device, cmd_name, fac, "DG_T_DEV")
        if cmd_comp is None:
            return None
        data = dict()
        if cmd_comp is None:
            return None
        dg = cmd_comp.find("Param[@key='DGTYPE']").get("value")
        data["dg"] = dg
        dg_xml, err = self.device_dg_mappings(device, dg)
        if dg_xml is None:
            return None
        deid = dg_xml.find("UdcMapping").get("data_element_id") if dg_xml.find("UdcMapping") is not None else None
        data['ld'] = deid
        data['val'] = None
        return data

    def cmd_data(self, device, cmd_name, fac, ao_do='do', manual=False):
        if ao_do == "ao":
            data = self.ao_command_data(device, cmd_name, fac)
        else:
            data = self.do_command_data(device, cmd_name, fac)
        if data is None:
            return None
        if manual:
            cmd_comp = self.find_command_component(device, cmd_name, fac, "CYUPDTPT")
            if cmd_comp is None:
                return None
            data["fac"] = cmd_comp.find("Param[@key='Fac']").get("value")
            data["udc"] = cmd_comp.find("Param[@key='UDC']").get("value")
        return data

    def device_dg_mappings(self, device_id, array_type):
        """
        :param device_id: CygNet Device name
        :param array_type: The array name inside the device
        :return: Tuple of the DataGroup UdcMappings Element and Error message
        """
        dgs = self.device_dgs_element(device_id)
        if dgs is None:
            return None, "Device {} Not Found".format(device_id)
        if dgs.find('./DataGroup/DataGroupAttributes/[DataGroupType="{}"].../UdcMappings'.format(array_type)) is None:
            return None, "Array {} not found in Device {}".format(array_type, device_id)
        return dgs.find('./DataGroup/DataGroupAttributes/[DataGroupType="{}"].../UdcMappings'.format(array_type)), ""

    def all_devices(self):
        devices = []
        for d in self.xml:
            dev_id = d.get("device_id")
            facs = []
            dgs = []
            for f in d.find("FacilityLinks"):
                facs.append(f.get("id"))
            for dg in d.find("DataGroups"):
                dgs.append(dg.find("DataGroupAttributes/DataGroupType").text)
            devices.append({
                "device_id": dev_id,
                "facility_links": facs,
                "data_groups": dgs,
            })
        return devices

    def all_mappings(self, device, data_group):
        maps = []
        mappings, error = self.device_dg_mappings(device, data_group)
        if mappings is not None:
            for m in mappings:
                maps.append({
                    "DEID": m.get("data_element_id"),
                    "facility": m.get("facility"),
                    "UDC": m.get("UDC")
                })
        else:
            maps.append({"ERROR": error})
        return maps

    def add_maps(self, device_id, array_type, maps, create=False, dtf=None):
        """
        Maps all supplied UDCs the given Device's Array.
        Checks all UCDs to see they already exist
        :param device_id: CygNet Device name
        :param array_type: The array name inside the device
        :param maps: List of UDCs to be mapped
        :param create: True to create False to skip
        :param dtf: DTF object
        :return: Any errors
        """
        mappings, err = self.device_dg_mappings(device_id, array_type)
        errs = []
        if mappings is None:
            if create:
                desc = dtf.get_array_description(array_type)
                if desc:
                    dg = self.add_datagroup(desc, array_type, device_id)
                    errs.append("{} DataGroup created for device: {}".format(array_type, device_id))
                    mappings, err = self.device_dg_mappings(device_id, array_type)
                else:
                    errs.append("{} Not Found in DTF".format(array_type))
                    return errs
            else:
                errs.append(err)
                return errs
        for m in maps:
            if mappings.find(".//UdcMapping[@UDC='{}'][@data_element_id='{}'][@facility='{}']".format(
                    m.udc,
                    m.data_id,
                    m.fac)
            ) is None:
                SubElement(mappings, "UdcMapping", {
                    "UDC": m.udc,
                    "data_element_id": m.data_id,
                    "facility": m.fac
                })
            else:
                errs.append("{} {} {} mapping already exists".format(m.udc, m.data_id, m.fac))
        return errs

    def add_datagroup(self, description, data_group_type, device_id):
        dg = DataGroup(description, device_id, data_group_type)
        current_dgs = self.device_dgs_element(device_id)
        current_dgs.append(dg.dg_element)
        return current_dgs

    @staticmethod
    def _ordinal_finder(fac_elem):
        first = len(fac_elem)
        while True:
            if fac_elem.find("./FacilityLink[@ordinal='{}']".format(str(first))) is not None:
                first += 1
            else:
                break
        return str(first)

    def add_facs(self, facs, device_id):
        """
        Addes all facs to the device's FacilityLinks Element
        :param facs: List of Facility names
        :param device_id: Device the facilities should be mapped too
        :return: Any errors
        """
        fac_elem = self.device_facs_element(device_id)
        log = []
        if fac_elem is not None:
            for f in facs:
                if fac_elem.find("./FacilityLink[@id='{}']".format(f)) is None:
                    SubElement(fac_elem, "FacilityLink", {"id": f, "ordinal": self._ordinal_finder(fac_elem)})
                    log.append("Facility {} was linkded to {} device".format(f, device_id))
        else:
            log.append("Device {} was not found to add facilities".format(device_id))
        return log

    def add_facility(self, facility, device_id):
        """
        Adds a facility to the device's FacilityLinks Element
        :param facility: Facility to be added
        :param device_id: Device the facilities should be mapped too
        :return: Any errors
        """
        fac_elem = self.device_facs_element(device_id)
        if fac_elem is not None:
            if fac_elem.find("./FacilityLink[@id='{}']".format(facility)) is None:
                SubElement(fac_elem, "FacilityLink", {"id": facility, "ordinal": self._ordinal_finder(fac_elem)})
                outcome = "Facility {} was linkded to {} device".format(facility, device_id)
            else:
                outcome = "{} is already linked in device {}".format(facility, device_id)
        else:
            outcome = "Device {} was not found to add facilities".format(device_id)
        return outcome

    def export_data(self, dtf_xml=False):
        """
        Export all UIS mappings for easy validation
        :return: Pandas DF of all UIS mappings
        """
        devs_dict = {
            "dev_id": [],
            "comm_id": [],
            "desc": [],
            "dg_type": [],
            "deid": [],
            "last_char": [],
            "fac": [],
            "udc": [],
            "reg": [],
            "bit1": [],
            "bit2": [],
            "dtype": []
        }
        for elem in self.xml:
            dev_id = elem.get("device_id")
            comm_id = elem.find("DeviceAttributes/CommunicationId1").text
            for data_group in elem.find("DataGroups"):
                desc = data_group.find("DataGroupAttributes/Description").text
                dg_type = data_group.find("DataGroupAttributes/DataGroupType").text
                for m in data_group.find("UdcMappings"):
                    deid = m.get("data_element_id")
                    if dtf_xml:
                        reg, bit, bit2 = dtf_xml.get_deid_tag(dg_type, deid)
                        dtype = dtf_xml.deid_datatype(dg_type, deid)
                    else:
                        reg = bit = bit2 = ""
                    devs_dict["dev_id"].append(dev_id)
                    devs_dict["comm_id"].append(comm_id)
                    devs_dict["desc"].append(desc)
                    devs_dict["dg_type"].append(dg_type)
                    devs_dict["deid"].append(deid)
                    devs_dict["last_char"].append(deid[-2:])
                    devs_dict["fac"].append(m.get("facility"))
                    devs_dict["udc"].append(m.get("UDC"))
                    devs_dict["reg"].append(reg)
                    devs_dict["bit1"].append(bit if bit else "")
                    devs_dict["bit2"].append(bit2 if bit2 else "")
                    devs_dict["dtype"].append(dtype if dtype else "")
        return pd.DataFrame(data=devs_dict)

    @staticmethod
    def _mapping_validator(pnts, point, tag, bit=False, bit2=False):
        if "[" in tag:
            tag_new = "{}:{}".format(tag.split("[")[0], tag.split("[")[1].split("]")[0])
        else:
            tag_new = tag
        try:
            dtf_bit = int(pnts.loc[point][1])
            dtf_bit2 = int(pnts.loc[point][2])
            dtf_tag = pnts.loc[point][0]
        except KeyError:
            return False, {"tag": "NotInImport", "bit": 0, "bit2": 0}
        if bit2:
            bits = [int(bit), int(bit2)]
            if tag_new != dtf_tag or dtf_bit not in bits or dtf_bit2 not in bits:
                return False, {"tag": dtf_tag, "bit": dtf_bit, "bit2": dtf_bit2}
        elif bit:
            if tag_new != pnts.loc[point][0] or int(bit) != int(pnts.loc[point][1]):
                return False, {"tag": dtf_tag, "bit": dtf_bit, "bit2": 0}
        else:
            if tag_new != pnts.loc[point][0]:
                return False, {"tag": dtf_tag, "bit": 0, "bit2": 0}
        return True, None

    def validate_mappings(self, dtf_xml, pnts):
        """
        Loop through every mapping in every data group in every device and check the
        point against a supplied list of points and where they should be mapped
        :param dtf_xml: DTF object to grap registers from
        :param pnts: pandas object with all points and their mappings
        :return: Log of errors
        """
        log = []
        for elem in self.xml:
            dev_id = elem.get("device_id")
            for data_group in elem.find("DataGroups"):
                dg_type = data_group.find("DataGroupAttributes/DataGroupType").text
                for m in data_group.find("UdcMappings"):
                    deid = m.get("data_element_id")
                    long_id = "{}_{}".format(m.get("facility"), m.get("UDC"))
                    tag, bit, bit2 = dtf_xml.get_deid_tag(dg_type, deid)
                    if tag is not None:
                        valid, vals = self._mapping_validator(pnts, long_id, tag, bit=bit, bit2=bit2)
                    else:
                        valid = False
                        vals = {"tag": "ORPHAN", "bit": False, "bit2": False}
                    if not valid:
                        log.append(
                            {
                                "device": dev_id,
                                "long_id": long_id,
                                "datagroup": dg_type,
                                "deid": deid,
                                "dtf_tag": tag,
                                "tag": vals["tag"],
                                "dtf_bit": bit,
                                "bit": vals["bit"],
                                "dtf_bit2": bit2,
                                "bit2": vals["bit2"]
                            }
                        )
        return log

    def import_commands(self, cmds, dtf_xml):
        errs = []
        for i, cmd in cmds.iterrows():
            device_id = cmd.get("device")
            facility = cmd.get("facility")
            name = cmd.get("name")
            data_group = cmd.get("data_group")
            comp_type = cmd.get("comp_type")
            update_fac = cmd.get("update_fac")
            udc = cmd.get("udc")
            site = cmd.get("site")
            service = cmd.get("service")
            utype = cmd.get("utype")
            value = cmd.get("value") if not math.isnan(cmd.get("value")) else False
            cmd_xml = self.find_command(device_id, name, facility)
            if cmd_xml is None:
                cmd_xml = self.create_command(device_id, name, facility, cmd.get("description"))
            if not cmd_xml:
                errs.append("Device {} not in xml".format(device_id))
            else:
                cmd_comp_xml = cmd_xml.find("CommandComponents")
                dg_exists, _ = self.device_dg_mappings(device_id, data_group)
                ord = len(cmd_comp_xml)
                if comp_type == "DG_T_DEV":
                    load = dtf_xml.get_ucc_param(data_group)
                    comp = Command.create_dg_t_dev_comp(ord, data_group, load, value)
                    cmd_comp_xml.append(comp)
                    if dg_exists is None:
                        desc = dtf_xml.get_array_description(data_group)
                        if desc:
                            dg = self.add_datagroup(description=desc, data_group_type=data_group, device_id=device_id)
                            errs.append("{} DataGroup created for device: {}".format(data_group, device_id))
                        else:
                            errs.append("{} Not Found in DTF".format(data_group))
                elif comp_type == "CYUPDTPT":
                    comp = Command.create_cyuptpt_comp(ord, update_fac, service, site, udc, utype)
                    cmd_comp_xml.append(comp)
        self.save()
        return errs

    def create_command(self, device_id, name, facility, desc):
        device_cmds = self.device_uis_element(device_id)
        if device_cmds is None:
            return False
        new_cmd = Command(name, facility, desc)
        device_cmds.append(new_cmd.command_element)
        return self.find_command(device_id, name, facility)

    def uis_commands(self, dtf_xml=False):
        """
        Format DDS XML to a usable Excel dataframe to for mapping validation
        Every component will have single line
        :return: Pandas DataFrame of all components in the xml
        """

        def _dg_type(s_cmd):
            dg = c.find("Param[@key='DGTYPE']").get("value")
            s_cmd["dev_id"] = dev_id
            s_cmd["comm_id"] = comm_id
            s_cmd["desc"] = cmd_decs
            s_cmd["UIS_fac"] = fac
            s_cmd["cmd_name"] = cmd_name
            s_cmd["comp_type"] = c_type
            s_cmd["comp_pos"] = c.get("position")
            s_cmd["DGORD"] = c.find("Param[@key='DGORD']").get("value")
            s_cmd["DGTYPE"] = dg
            xpath = c.xpath("Param[starts-with(@key,'L')]")[0] if len(
                c.xpath("Param[starts-with(@key,'L')]")) != 0 else None
            if xpath is not None:
                ld = xpath.get("key")
                if dtf_xml:
                    tag = dtf_xml.deid_tagname(dg, ld)
                    dtype = dtf_xml.deid_datatype(dg, ld)
                    s_cmd["Register"] = tag
                    s_cmd["datatype"] = dtype
                s_cmd["LD"] = xpath.get("key")
                s_cmd["Value"] = xpath.get("value")
            else:
                dg_xml, err = self.device_dg_mappings(dev_id, dg)
                if dg_xml is None:
                    return None
                if dg_xml.find("UdcMapping") is not None:
                    deid = dg_xml.find("UdcMapping").get("data_element_id")
                else:
                    deid = dtf_xml.get_ucc_param(dg) if dtf_xml else ""
                s_cmd["LD"] = deid
                if dtf_xml:
                    tag = dtf_xml.deid_tagname(dg, deid)
                    dtype = dtf_xml.deid_datatype(dg, deid)
                    s_cmd["Register"] = tag
                    s_cmd["datatype"] = dtype
            append_cmd(s_cmd)

        def _cyupdtpt(s_cmd):
            s_cmd["dev_id"] = dev_id
            s_cmd["comm_id"] = comm_id
            s_cmd["desc"] = cmd_decs
            s_cmd["UIS_fac"] = fac
            s_cmd["cmd_name"] = cmd_name
            s_cmd["comp_type"] = c_type
            s_cmd["comp_pos"] = c.get("position")
            for param in c:
                s_cmd[param.get("key")] = param.get("value")
            append_cmd(s_cmd)

        def append_cmd(cmd_sing):
            for k, v in cmd_sing.items():
                try:
                    cmd_dict[k].append(v)
                except KeyError:
                    print(k, v)
        cmd_dict = {
            "dev_id": [],
            "comm_id": [],
            "desc": [],
            "UIS_fac": [],
            "cmd_name": [],
            "comp_type": [],
            "comp_pos": [],
            "DGORD": [],
            "DGTYPE": [],
            "LD": [],
            "Fac": [],
            "FOnErr": [],
            "Serv": [],
            "Site": [],
            "UDC": [],
            "UType": [],
            "Value": [],
            "Register": [],
            "datatype": []
        }
        for elem in self.xml:
            dev_id = elem.get("device_id")
            comm_id = elem.find("DeviceAttributes/CommunicationId1").text
            for uis in elem.find("UisCommands"):
                cmd_name = uis.find('CommandAttributes/Name').text
                cmd_decs = uis.find('CommandAttributes/Description').text
                fac = uis.find('CommandAttributes/Facility').text
                for c in uis.find("CommandComponents"):
                    _cmd = {
                        "dev_id": "",
                        "comm_id": "",
                        "desc": "",
                        "UIS_fac": "",
                        "cmd_name": "",
                        "comp_type": "",
                        "comp_pos": "",
                        "DGORD": "",
                        "DGTYPE": "",
                        "LD": "",
                        "Fac": "",
                        "FOnErr": "",
                        "Serv": "",
                        "Site": "",
                        "UDC": "",
                        "UType": "",
                        "Value": "",
                        "Register": "",
                        "datatype": ""
                    }
                    c_type = c.get("type")
                    if c_type == "DG_T_DEV" or c_type == "DG_F_DEV":
                        _dg_type(_cmd)
                    elif c_type == "CYUPDTPT":
                        _cyupdtpt(_cmd)
        return pd.DataFrame(data=cmd_dict)

    def mapped_fac_check(self):
        # TODO: return just a list of facilities, not every mapping.
        """
        :return: A list and their devices that are not mapped correctly
        """
        unmapped = []
        for elem in self.xml:
            dev_id = elem.get("device_id")
            for data_group in elem.find("DataGroups"):
                for m in data_group.find("UdcMappings"):
                    f = m.get("facility")
                    unmapped.append({
                        "facility": f,
                        "device": dev_id
                    }) if elem.find("FacilityLinks/FacilityLink[@id='{}']".format(f)) is None else None
        return unmapped

    def fac_exists_check(self, facs):
        """
        :param facs:
        :return: A list of facilities and their device that do no exist in the supplied Facility list
        """
        dne = []
        for elem in self.xml:
            dev_id = elem.get("device_id")
            for f in elem.find("FacilityLinks"):
                if f.get("id") not in facs:
                    dne.append({
                        "device": dev_id,
                        "facility": f.get("id")
                    })
        return dne

    def correct_dev_check(self):
        """
        Check the first 4 letters in every facility and check that it matches with the first 4 of the device
        :return: List of all Points that do not match
        """
        non_matches = []
        for elem in self.xml:
            dev_id = elem.get("device_id").split("_")[0]
            dev_full = elem.get("device_id")
            for data_group in elem.find("DataGroups"):
                dg_type = data_group.find("DataGroupAttributes/DataGroupType").text
                for m in data_group.find("UdcMappings"):
                    if m.get("facility").split("_")[0] != dev_id:
                        non_matches.append({
                            "deid": m.get("data_element_id"),
                            "facility": m.get("facility"),
                            "udc": m.get("UDC"),
                            "dg_type": dg_type,
                            "device": dev_full,
                        })
        return non_matches

    def find_orphans(self, dtf):
        orphans = []
        for elem in self.xml:
            dev_id = elem.get("device_id")
            for data_group in elem.find("DataGroups"):
                dg_type = data_group.find("DataGroupAttributes/DataGroupType").text
                for m in data_group.find("UdcMappings"):
                    chck = dtf.check_dg_element(dg_type, m.get("data_element_id"))
                    if not chck:
                        print(m.get("data_element_id"), m.get("facility"), m.get("UDC"))
                        orphans.append({
                            "device": dev_id,
                            "array": dg_type,
                            "deid": m.get("data_element_id")
                        })
        return orphans

    def deid_exists(self, array_name, deids):
        mappings = self.xml.findall(
            "./Device/DataGroups/DataGroup/DataGroupAttributes/[DataGroupType='{}']../UdcMappings".format(
                array_name)
        )
        for a in mappings:
            a_deieds = [d.get("data_element_id") for d in a]
            deids = list(set(deids) - set(a_deieds))
        return deids

    def mapping_excel_import(self, mappings, dtfxml, deid_only, add_dgs=False):
        """
        Add all mappings supplied in pandas object (create pandas object in method?)
        :param mappings: pandas dataframe with all mappings
        :param dtfxml: DTF Object used to check deids
        :param deid_only:
        :param add_dgs: DTF Object used to check deids
        :return: List of errors (strings) that occurred while mapping points
        """
        devices = mappings.device.unique()
        errs = []
        for d in devices:
            dev_points = mappings.loc[mappings['device'] == d]
            dev_arr = dev_points.array.unique()
            facs = []
            if self.check_device(d) is not None:
                for da in dev_arr:
                    arr_points = dev_points.loc[dev_points['array'] == da]
                    maps = []
                    for i, p in arr_points.iterrows():
                        udc, pnt_err = UdcMap.safe_create(dtfxml, p, da, deid_only)
                        maps.append(udc) if not pnt_err else errs.append(udc)
                        facs.append(p["facilityid"]) if p["facilityid"] not in facs else None
                    map_log = self.add_maps(d, da, maps, add_dgs, dtfxml)
                    fac_log = self.add_facs(facs, d)
                    errs = errs + map_log + fac_log
            else:
                errs.append("Device {} is not in XML".format(d))
        self.save()
        return errs

    @classmethod
    def mappings_template(cls):
        sheets = list()
        sheets.append({
            'device': ["ABIL_DEV", "ANDW_DEV"],
            'type': ['D', 'A'],
            'facilityid': ['ABIL_PUMP1', 'ANDW_A_PSTATION'],
            'uniformdatacode': ['PSTATUS', 'FSPFB'],
            'bits': [2, 1],
            'array': ['N40', 'AI_ARRAY'],
            'deid': ['MB000405', 'N4X00'],
            'tag': ['N40', 'AI_MT_TK_N4X'],
            'register': [0, 0],
            'bit1': [4, 0],
            'bit2': [5, None]
        })
        return cls.template_export(sheets)

    @classmethod
    def pnt_validation_template(cls):
        sheets = list()
        sheets.append({
            'point': ["ABIL_A_PSTATION_PSTATIC", "ABIL_PUMP2_PSTATUS"],
            'register': ['0', "N40:3"],
            'bit': ['0', '15'],
            'bit2': ['0', '0'],

        })
        return cls.template_export(sheets)

    def export_mappings(self, dtf_xml=None):
        df_pnt = self.export_data(dtf_xml)
        df_cmd = self.uis_commands(dtf_xml)
        sio = BytesIO()
        writer = pd.ExcelWriter(sio, engine="xlsxwriter")
        df_pnt.to_excel(writer, sheet_name="PNTS")
        df_cmd.to_excel(writer, sheet_name="CMDS")
        writer.save()
        writer.close()
        sio.seek(0)
        return sio.getvalue()


class DataGroup:
    def __init__(self, description, fac_id, dg_type):
        self.description = description
        self.fac_id = fac_id
        self.dg_type = dg_type
        self.dg_element = None
        self.create_element()

    def create_element(self):
        dg_xml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils", "DataGroup.xml")
        tree = etree.parse(dg_xml_path)
        root = tree.getroot()
        root.find("DataGroupAttributes/Description").text = self.description
        root.find("DataGroupAttributes/FacilityId").text = self.fac_id
        root.find("DataGroupAttributes/DataGroupType").text = self.dg_type
        self.dg_element = root

    @property
    def udc_maps(self):
        return self.dg_element.find("UdcMappings")


class Command:
    def __init__(self, name, fac_id, description):
        self.name = name
        self.fac_id = fac_id
        self.description = description
        self.command_element = None
        self.create_element()

    def create_element(self):
        dg_xml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils", "Command.xml")
        tree = etree.parse(dg_xml_path)
        root = tree.getroot()
        root.find("CommandAttributes/Name").text = self.name
        root.find("CommandAttributes/Facility").text = self.fac_id
        root.find("CommandAttributes/Description").text = self.description
        self.command_element = root

    @classmethod
    def create_dg_t_dev_comp(cls, pos, data_group, load=False, value=False):
        component = etree.Element("Component", {"type": "DG_T_DEV", "position": str(pos)})
        SubElement(component, "Param", {"key": "DGORD", "value": "0"})
        SubElement(component, "Param", {"key": "DGTYPE", "value": data_group})
        if load and value:
            SubElement(component, "Param", {"key": load, "value": str(int(value))})
        return component

    @classmethod
    def create_cyuptpt_comp(cls, pos, fac, service, site, udc, utype):
        component = etree.Element("Component", {"type": "CYUPDTPT", "position": str(pos)})
        SubElement(component, "Param", {"key": "DGORD", "value": "-1"})
        SubElement(component, "Param", {"key": "DGTYPE", "value": "n/a"})
        SubElement(component, "Param", {"key": "Fac", "value": fac})
        SubElement(component, "Param", {"key": "FOnErr", "value": "1"})
        SubElement(component, "Param", {"key": "Serv", "value": service})
        SubElement(component, "Param", {"key": "Site", "value": site})
        SubElement(component, "Param", {"key": "UDC", "value": udc})
        SubElement(component, "Param", {"key": "UType", "value": str(int(utype))})
        return component


class UdcMap:
    """
    Used to build UdcMappings in the DeviceDef class
    """

    def __init__(self, udc, data_id, fac):
        self.udc = udc
        self.data_id = data_id
        self.fac = fac

    @classmethod
    def safe_create(cls, dtf_xml, row, dev_array, deid_only):
        # TODO: Scrub udc data. (None for bit)
        """
        :param dtf_xml: DTF class
        :param row: Dict of {'facilityid': '','register':'','uniformdatacode':'','tag':''}
        :param dev_array: array we are looking to add a mapping too
        :param deid_only: bool that tells whether or not to build UDC from
        :return: Tuple of UDC and error bool, (if error, returns Error message)
        """
        if row["type"] == "A":
            if deid_only:
                deid = row["deid"] if dtf_xml.check_dg_element(row["array"], row["deid"]) else False
            else:
                deid = dtf_xml.get_analog_deid(dev_array, row["tag"], str(int(row["register"])))
            if deid:
                _udc, err = UdcMap(row["uniformdatacode"], deid, row["facilityid"]), False
            else:
                _udc, err = "*DEID Not found* tagname: {}[{}], Array: {}, UDC: {} FAC: {}".format(
                    row["tag"], row["register"], dev_array,
                    row["uniformdatacode"],
                    row["facilityid"]
                ), True
        elif row["type"] == "D":
            if dtf_xml.check_dg_element(row["array"], row["deid"]):
                _udc, err = cls(row["uniformdatacode"], row["deid"], row["facilityid"]), False
            else:
                _udc, err = "*DEID Not found* DEID: {}, Array {}, UDC: {} FAC: {}".format(
                    row["deid"],
                    dev_array,
                    row["uniformdatacode"],
                    row["facilityid"]
                ), True
        else:
            _udc, err = "Point type is neither A or D", True
        return _udc, err

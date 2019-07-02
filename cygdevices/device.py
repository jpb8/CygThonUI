from lxml import etree
from lxml.etree import SubElement
import pandas as pd
from io import BytesIO


class DeviceDef:
    def __init__(self, device_xml_path):
        self.xml = None
        self.device_xml_path = device_xml_path
        self.create_xml()

    def create_xml(self):
        """
        Sets the xml prop to an ETREE root with the supplied xml file
        :return:
        """
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(self.device_xml_path, parser)
        root = tree.getroot()
        self.xml = root

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
            return None, "Array {} not found in Device {}".format(device_id, array_type)
            # dg = DataGroup(device_id, device_id, array_type)
            # dgs.append(dg.dg_element)
            # print("appended {} {} DataGroup".format(device_id, array_type))
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

    def add_maps(self, device_id, array_type, maps):
        """
        Maps all supplied UDCs the given Device's Array.
        Checks all UCDs to see they already exist
        :param device_id: CygNet Device name
        :param array_type: The array name inside the device
        :param maps: List of UDCs to be mapped
        :return: Any errors
        """
        mappings, err = self.device_dg_mappings(device_id, array_type)
        errs = []
        if mappings is None:
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

    def save(self):
        file = open(self.device_xml_path, "wb")
        file.write(etree.tostring(self.xml, pretty_print=True))
        file.close()

    def export_data(self):
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
            "udc": []
        }
        for elem in self.xml:
            dev_id = elem.get("device_id")
            comm_id = elem.find("DeviceAttributes/CommunicationId1").text
            for data_group in elem.find("DataGroups"):
                desc = data_group.find("DataGroupAttributes/Description").text
                dg_type = data_group.find("DataGroupAttributes/DataGroupType").text
                for m in data_group.find("UdcMappings"):
                    devs_dict["dev_id"].append(dev_id)
                    devs_dict["comm_id"].append(comm_id)
                    devs_dict["desc"].append(desc)
                    devs_dict["dg_type"].append(dg_type)
                    devs_dict["deid"].append(m.get("data_element_id"))
                    devs_dict["last_char"].append(m.get("data_element_id")[-2:])
                    devs_dict["fac"].append(m.get("facility"))
                    devs_dict["udc"].append(m.get("UDC"))
        return pd.DataFrame(data=devs_dict)

    def uis_commands(self):
        """
        Format DDS XML to a usable Excel dataframe to for mapping validation
        Every component will have single line
        :return: Pandas DataFrame of all components in the xml
        """

        def _dg_type(s_cmd):
            s_cmd["dev_id"] = dev_id
            s_cmd["comm_id"] = comm_id
            s_cmd["desc"] = cmd_decs
            s_cmd["UIS_fac"] = fac
            s_cmd["cmd_name"] = cmd_name
            s_cmd["comp_type"] = c_type
            s_cmd["comp_pos"] = c.get("position")
            s_cmd["DGORD"] = c.find("Param[@key='DGORD']").get("value")
            s_cmd["DGTYPE"] = c.find("Param[@key='DGTYPE']").get("value")
            xpath = c.xpath("Param[starts-with(@key,'L')]")[0] if len(
                c.xpath("Param[starts-with(@key,'L')]")) != 0 else None
            if xpath is not None:
                s_cmd["LD"] = xpath.get("key")
                s_cmd["Value"] = xpath.get("value")
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
                cmd_dict[k].append(v)

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
                if f not in facs:
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
                        orphans.append({
                            "device": dev_id,
                            "array": dg_type,
                            "deid": m.get("data_element_id")
                        })
        return orphans

    def mapping_excel_import(self, mappings, dtfxml, deid_only):
        """
        Add all mappings supplied in pandas object (create pandas object in method?)
        :param mappings: pandas dataframe with all mappings
        :param dtfxml: DTF Object used to check deids
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
                    map_log = self.add_maps(d, da, maps)
                    fac_log = self.add_facs(facs, d)
                    errs = errs + map_log + fac_log
            else:
                errs.append("Device {} is not in XML".format(d))
        self.save()
        return errs

    def export_mappings(self):
        df_pnt = self.export_data()
        df_cmd = self.uis_commands()
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
        tree = etree.parse("utils/DataGroup.xml")
        root = tree.getroot()
        root.find("DataGroupAttributes/Description").text = self.description
        root.find("DataGroupAttributes/FacilityId").text = self.fac_id
        root.find("DataGroupAttributes/DataGroupType").text = self.dg_type
        self.dg_element = root

    @property
    def udc_maps(self):
        return self.dg_element.find("UdcMappings")


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
        """
        :param dtf_xml: DTF class
        :param row: Dict of {'facilityid': '','bit':'','uniformdatacode':'','indexed':''}
        :param dev_array: array we are looking to add a mapping too
        :param deid_only: bool that tells whether or not to build UDC from
        :return: Tuple of UDC and error bool, (if error, returns Error message)
        """
        if row["type"] == "A" and not deid_only:
            deid = dtf_xml.get_analog_deid(dev_array, row["indexed"], str(int(row["bit"])))
            if deid:
                _udc, err = UdcMap(row["uniformdatacode"], deid, row["facilityid"]), False
            else:
                _udc, err = "*DEID Not found* tagname: {}[{}], Array: {}, UDC: {} FAC: {}".format(
                    row["indexed"], row["bit"], dev_array,
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

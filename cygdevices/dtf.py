from lxml.etree import SubElement
from lxml import etree
import pandas as pd

from .xml import XmlFile
import math


class DTF(XmlFile):
    @property
    def data_groups(self):
        return self.xml.find("dataGroups")

    @property
    def def_data_groups(self):
        if self.xml.find("defDataGroups") is None:
            SubElement(self.xml, "defDataGroups")
        return self.xml.find("defDataGroups")

    def find_dg_element(self, array_type, element):
        """
        Finds the DEID in an array
        :param array_type:
        :param element: DEID
        :return:
        """
        return self.xml.find('dataGroups/{}/dgElements/{}'.format(array_type, element))

    def check_dg_element(self, array_type, element):
        return True if self.find_dg_element(array_type, element) is not None else False

    def get_data_group(self, array_type):
        return self.xml.find('dataGroups/{}'.format(array_type))

    def get_analog_deid(self, array_name, index, reg):
        """
        :param array_name: CygNet Array Name
        :param index: First part of tagname DEID attr
        :param reg: Device register
        :return: DEID Tag
        """
        tag = "{}[{}]".format(index, reg)
        if self.xml.find("dataGroups/{}/dgElements/*[@tagname='{}']".format(array_name, tag)) is None:
            deid = self.xml.find("dataGroups/{}/dgElements/*[@elemAddr='{}']".format(array_name, tag))
        else:
            deid = self.xml.find("dataGroups/{}/dgElements/*[@tagname='{}']".format(array_name, tag))
        return deid.tag if deid is not None else False

    def get_analog_tag(self, array_name, deid):
        tag = self.xml.find("dataGroups/{}/dgElements/{}".format(array_name, deid))
        if tag is None:
            return None
        return tag.get("tagname") if tag.get("tagname") is not None else tag.get("elemAddr")

    def get_multibit_tag(self, array_name, deid):
        tag = self.xml.find("dataGroups/{}/dgElements/{}".format(array_name, deid))
        if tag is None:
            return None, None, None
        refs = tag.findall("ref")
        if len(refs) < 2:
            return None, None, None
        tag_name, bit = self.get_digital_tag(array_name, refs[0].get("deid"))
        tag2, bit2 = self.get_digital_tag(array_name, refs[1].get("deid"))
        return tag_name, bit, bit2

    def get_digital_tag(self, array_name, deid):
        tag = self.xml.find("dataGroups/{}/dgElements/{}".format(array_name, deid))
        if tag is None:
            return None, None
        parent_tag = self.xml.find("dataGroups/{}/dgElements/{}".format(array_name, tag.get("ref")))
        if parent_tag is None:
            return None, None
        tag_name = parent_tag.get("tagname") if parent_tag.get("tagname") is not None else parent_tag.get("elemAddr")
        bit = tag.get("bPos")
        return tag_name, bit

    def get_deid_tag(self, array_name, deid):
        if deid[:2] in ["MB", "VS", "PS"]:
            tag, bit, bit2 = self.get_multibit_tag(array_name, deid)
        elif deid[0] == "D":
            tag, bit = self.get_digital_tag(array_name, deid)
            bit2 = False
        else:
            tag = self.get_analog_tag(array_name, deid)
            bit = False
            bit2 = False
        return tag, bit, bit2

    def get_array_description(self, array_name):
        return self.data_groups.find(array_name).get("niceName") if self.data_groups.find(
            array_name) is not None else False

    def get_ucc_param(self, array_name):
        array_xml = self.data_groups.find(array_name)
        if array_xml is None:
            return None
        ucc_params = array_xml.find("uccSendParms")
        if ucc_params is None:
            return None
        for ucc in ucc_params:
            return ucc.tag

    def all_arrays(self):
        arrays = []
        for dg in self.data_groups:
            arrays.append({
                "name": dg.tag,
                "niceName": dg.get("niceName")
            })
        return arrays

    def get_discrete_deid(self, array_name, index, index2=None):
        pass

    def delete_datagroup(self, dg_name):
        dg = self.data_groups.find(dg_name)
        def_dg = self.def_data_groups.find(dg_name)
        if dg:
            self.data_groups.remove(dg)
        if def_dg:
            self.def_data_groups.remove(def_dg)
        self.save()

    def create_ai_deid(self, array_root, deid, tagname, data_type="r4"):
        SubElement(array_root, deid, {
            "niceName": tagname,
            "desc": tagname,
            "tagname": tagname,
            "type": data_type
        })

    def deid_tagname(self, array, deid):
        dg_elm = self.find_dg_element(array, deid)
        if dg_elm is None:
            return None
        if self.find_dg_element(array, deid).get("tagname") is not None:
            tag = self.find_dg_element(array, deid).get("tagname")
        else:
            tag = self.find_dg_element(array, deid).get("elemAddr")
        return tag

    def deid_datatype(self, array, deid):
        dg_elm = self.find_dg_element(array, deid)
        if dg_elm is None:
            return None
        return self.find_dg_element(array, deid).get("type")

    def create_array(self, name, nice_name):
        new_array = SubElement(self.data_groups, name, {
            "niceName": nice_name,
            "udcCat": "~UDCALL",
            "canSend": "false",
            "canRecv": "true",
            "uccSend": "false",
            "uccRecv": "true",
            "udcDefFac": "true",
            "devDG": "false",
            "baseOrd": "0",
            "maxCnt": "1"
        })
        return new_array

    @staticmethod
    def _build_ai_deid(deid_base, number):
        num_len = len(str(number))
        if num_len == 1:
            return "{}00{}".format(deid_base, number)
        elif num_len == 2:
            return "{}0{}".format(deid_base, number)
        else:
            return "{}{}".format(deid_base, number)

    @staticmethod
    def _build_di_deid(deid_base, array_num, bit_num):
        num_str = str(bit_num) if len(str(bit_num)) > 1 else "0{}".format(str(bit_num))
        return "{}{}{}".format(deid_base, array_num, str(num_str))

    def add_full_array(self, array_name, nice_name, tag_name, data_type, deid, diai, bits, start, stop):
        new_array = self.create_array(array_name, nice_name)
        if diai == "ai":
            for i in range(start, stop):
                full_deid = self._build_ai_deid(deid, i)
                SubElement(new_array, full_deid, {
                    "niceName": "{} {}".format(nice_name, i),
                    "desc": "{} {}".format(nice_name, i),
                    "tagname": "{}[{}]".format(tag_name, i),
                    "type": data_type
                })
        else:
            for i in range(start, stop):
                array_num = "0{}".format(str(i)) if len(str(i)) < 2 else str(i)
                array_deid = "{}{}R".format(deid, array_num)
                SubElement(new_array, array_deid, {
                    "niceName": "{} {}".format(nice_name, i),
                    "desc": "{} {}".format(nice_name, i),
                    "tagname": "{}[{}]".format(tag_name, i),
                    "type": data_type
                })
                for j in range(bits):
                    full_deid = self._build_di_deid(deid, array_num, j)
                    SubElement(new_array, full_deid, {
                        "desc": "{} Array {} Bit {}".format(nice_name, i, j),
                        "ref": array_deid,
                        "type": "boolean",
                        "bPos": str(j)
                    })
        self.save()

    def unused_deids(self, dds):
        unused = []
        for dg in self.data_groups:
            array_name = dg.tag
            deids = [deid.tag for deid in dg.find("dgElements")]
            unused_deids = dds.deid_exists(array_name, deids)
            for u in unused_deids:
                unused.append({"ARRAY": array_name, "DEID": u})
        return unused

    @staticmethod
    def _convert_generic_export(data, keys):
        """
        Converts the data structure from generic_export method to pandas readable data structure
        start => list of dicts
        end => dict of lists
        :param data: List of dictionaries with variable keys
        :param keys: Unique list of keys in all items in data
        :return: A dictionary of list
        """
        export_data = {}
        for k in keys:
            export_data[k] = []
        for item in data:
            for k in keys:
                export_data[k].append(item.get(k, ""))
        return export_data

    @staticmethod
    def _pull_mb_readblocks(dg):
        rbs = {}
        if dg.find("modbusReadBlocks"):
            for rb in dg.find("modbusReadBlocks"):
                block_num = str(rb.tag).replace("block", "")
                rbs[block_num] = {}
                for k, v in rb.items():
                    rbs[block_num][k] = v
        return rbs

    def generic_export(self):
        data_groups = self.xml.find('dataGroups')
        deid_keys = ["array_id", "deid"]
        dg_keys = ["id"]
        deid_data = []
        dg_data = []
        for elem in data_groups:
            rbs = {}
            if elem.find("modbusReadBlocks"):
                rbs = self._pull_mb_readblocks(elem)
            if elem.find("dgElements"):
                curr_elm = elem.find("dgElements")
                dg_dict = {"id": elem.tag}
                dtype = curr_elm.get("type")
                for k, v in elem.items():
                    if k not in dg_keys:
                        dg_keys.append(k)
                    dg_dict[k] = v
                dg_data.append(dg_dict)
                for deid in elem.find("dgElements"):
                    deid_dict = {"deid": deid.tag, "array_id": elem.tag}
                    for k, v in deid.items():
                        if k not in deid_keys:
                            deid_keys.append(k)
                        deid_dict[k] = v
                    if "type" not in deid_dict:
                        deid_dict["type"] = dtype
                    if "regDef" in deid_dict:
                        rb_num = str(deid_dict["regDef"].split(":")[0])
                        if rb_num in rbs:
                            deid_dict.update(rbs[rb_num])
                            for k in rbs[rb_num].keys():
                                deid_keys.append(k) if k not in deid_keys else deid_keys
                    deid_data.append(deid_dict)
        dg_export_data = self._convert_generic_export(dg_data, dg_keys)
        deid_export_data = self._convert_generic_export(deid_data, deid_keys)
        return self.template_export([dg_export_data, deid_export_data])

    def create_array_excel(self, type=None):
        arrs = {"id": [], "niceName": [], "appId": []}
        dg_elems = {"deid": [], "array_id": [], "tagName": [], "niceName": [], "regNum": [], "desc": [], "dataType": [],
                    "udc": []}
        if not type:
            data_groups = self.xml.find('dataGroups')
            for elem in data_groups:
                arrs["id"].append(elem.tag)
                arrs["niceName"].append(elem.get("niceName"))
                arrs["appId"].append(elem.get("appId"))
                if elem.find("dgElements"):
                    curr_elm = elem.find("dgElements")
                    data_type = curr_elm.get("type")
                    for died in elem.find("dgElements"):
                        if died.get("type"):
                            data_type = died.get("type")
                        dg_elems["deid"].append(died.tag)
                        dg_elems["array_id"].append(elem.tag)
                        dg_elems["tagName"].append(died.get("tagname"))
                        dg_elems["regNum"].append(died.get("regNum"))
                        dg_elems["niceName"].append(died.get("niceName"))
                        dg_elems["desc"].append(died.get("desc"))
                        dg_elems["dataType"].append(data_type)
                        dg_elems["udc"].append(died.get("udc"))
        return self.template_export([arrs, dg_elems])

    def import_datagroups(self, data_elements, reg_gap, modbus=False):
        error_df = self._check_dg_excel_import(data_elements, modbus)
        data_elements.drop(data_elements.index[[tuple(error_df.index.values)]], inplace=True)
        data_groups_xml = self.data_groups
        data_groups = data_elements.data_group.unique()
        def_data_groups = self.def_data_groups
        for dg in data_groups:
            deids = data_elements.loc[data_elements["data_group"] == dg]
            nicename = dg
            if "nice_name" in deids:
                nicename = deids['nice_name'].iloc[0]
            dg_xml = self.get_data_group(dg)
            if dg_xml is None:
                dg_xml = DataGroup(dg.strip(), nicename.strip(), modbus)
                dg_xml.add_deids(deids, reg_gap)
                data_groups_xml.append(dg_xml.xml)
                SubElement(def_data_groups, dg)
            else:
                dg_xml = DataGroup(dg.strip(), nicename.strip(), modbus, xml=dg_xml)
                dg_xml.add_deids(deids, reg_gap)
        self.save()
        error_df.fillna('None', inplace=True)
        return error_df.to_dict('records'), self.all_arrays()

    @staticmethod
    def _check_dg_excel_import(data_elements, modbus=False):
        if modbus:
            reg_str_df = data_elements.loc[~data_elements['reg_num'].astype(str).str.isdigit()]
            reg_str_df["error"] = "reg_num must be integer"
        bit_str_df = data_elements.dropna(subset=['bit'])
        bit_str_df = bit_str_df.loc[~data_elements['bit'].astype(str).str.isnumeric()]
        bit_str_df["error"] = "bit must be integer"
        if modbus:
            return pd.concat([reg_str_df, bit_str_df])
        return bit_str_df


class DataGroup:
    def __init__(self, name, nice_name, modbus=False, xml=None):
        self.name = name
        self.nice_name = nice_name
        self.modbus = modbus
        self.data_name = "regNum" if modbus else "tagname"
        self.data_name_excel = "reg_num" if modbus else "tagname"
        if xml is None:
            self.xml = self.create_datagroup_xml()
        else:
            self.xml = xml

    def create_datagroup_xml(self):
        dg_attrs = {"niceName": self.nice_name, "canSend": "true", "canRecv": "true", "uccSend": "true",
                    "uccRecv": "true"}
        if self.modbus:
            dg_attrs["devDG"] = "false"
        dg = etree.Element(self.name, dg_attrs)
        SubElement(dg, "dgElements", {"type": "r4"})
        if self.modbus:
            SubElement(dg, "modbusReadBlocks")
        return dg

    def add_deids(self, deids, reg_gap):
        dg_elems = self.xml.find("dgElements")
        if self.modbus:
            analog_df = deids[(deids["dtype"] != "boolean") | (deids["bit"].isna())]
        else:
            analog_df = deids[(deids["dtype"] != "boolean") | (deids["bit"].isna())]
        digital_df = deids[(deids["dtype"] == "boolean") & (deids["bit"].notna())]
        self._add_analongs(dg_elems, analog_df)
        if self.modbus:
            self._add_digitals_modbus(dg_elems, digital_df)
            regs_df = deids[["reg_num", "offset", "func_code", "reg_byte_len"]].drop_duplicates()
            self._add_read_blocks(regs_df, reg_gap)
        else:
            self._add_digitals(dg_elems, digital_df)

    def _add_analongs(self, dg_elems, analog_df):
        for i, deid in analog_df.iterrows():
            dataloc = str(deid.get(self.data_name_excel)).strip()
            desc = str(deid.get("description")).strip()
            dtype = str(deid.get("dtype")).strip()
            udc = str(deid.get("udc")).strip() if not pd.isna(deid.get("udc")) else None
            read_only = str(deid.get("read_only")).strip() if not pd.isna(deid.get("read_only")) else None
            attrs = {"desc": desc, self.data_name: str(dataloc), "type": dtype if dtype != "digital" else "ui2"}
            if udc:
                attrs["udc"] = udc
            if read_only is not None:
                attrs["readOnly"] = "true" if read_only else "false"
            SubElement(dg_elems, str(deid.get("deid")).strip(), attrs)

    @staticmethod
    def _add_bits(dg_elems, ref):
        for i in range(0, 16):
            bit_str = "0{}".format(i) if i < 10 else str(i)
            attrs = {"desc": "Reg {} bit {}".format(ref, bit_str), "ref": ref, "bPos": str(i), "type": "Boolean"}
            SubElement(dg_elems, "{}B{}".format(ref, bit_str), attrs)

    def _add_digitals_modbus(self, dg_elems, digital_df):
        registers = digital_df.reg_num.unique()
        for reg in registers:
            attrs = {"desc": "Digital Registers {}".format(reg), "regNum": str(reg), "type": "ui2"}
            SubElement(dg_elems, "R{}".format(reg), attrs)
            reg_digitals = digital_df[digital_df["reg_num"] == reg]
            bits = reg_digitals.bit.unique()
            for i in range(0, 16):
                bit_str = "0{}".format(i) if i < 10 else str(i)
                if i in bits:
                    bit_row = reg_digitals[reg_digitals["bit"] == i].iloc[0]
                    desc = bit_row.get("description")
                    udc = bit_row.get("udc") if not pd.isna(bit_row.get("udc")) else None
                    if udc:
                        attrs = {"desc": desc, "ref": "R{}".format(reg), "bPos": str(i), "type": "Boolean", "udc": udc}
                    else:
                        attrs = {"desc": desc, "ref": "R{}".format(reg), "bPos": str(i), "type": "Boolean"}
                else:
                    attrs = {"desc": "Reg {} Bit {}".format(reg, bit_str),
                             "ref": "R{}".format(reg), "bPos": str(i), "type": "Boolean"}
                SubElement(dg_elems, "R{}B{}".format(reg, bit_str), attrs)

    def _add_digitals(self, dg_elems, digital_df):
        registers = digital_df.tagname.unique()
        for i, reg in enumerate(registers):
            attrs = {"desc": "Dig Reg {}".format(str(reg).strip()), "tagname": str(reg).strip(), "type": "ui4",
                     "hidden": "true"}
            reg_deid = "E1_{}".format(str(i))
            SubElement(dg_elems, "E1_{}".format(str(i)), attrs)
            reg_digitals = digital_df[digital_df["tagname"] == reg]
            bits = reg_digitals.bit.unique()
            for bit in bits:
                bit_row = reg_digitals[reg_digitals["bit"] == bit].iloc[0]
                desc = str(bit_row.get("description")).strip()
                bit_deid = str(bit_row.get("deid")).strip()
                udc = str(bit_row.get("udc")).strip() if not pd.isna(bit_row.get("udc")) else None
                if udc:
                    attrs = {"desc": desc, "ref": reg_deid, "bPos": str(bit), "type": "boolean", "udc": udc}
                else:
                    attrs = {"desc": desc, "ref": reg_deid, "bPos": str(bit), "type": "boolean"}
                SubElement(dg_elems, bit_deid, attrs)

    def _add_read_blocks(self, register_numbs, reg_gap):
        blocks = self.xml.find("modbusReadBlocks")
        block_number = 1
        register_numbs.sort_values(by=["reg_num"], inplace=True, ascending=True)
        reg_numb = register_numbs["reg_num"].iloc[0]
        for i in range(1, len(register_numbs.index)):
            if ((register_numbs["reg_num"].iloc[i] - reg_gap) > register_numbs["reg_num"].iloc[i - 1] or
                    register_numbs["offset"].iloc[i] != register_numbs["offset"].iloc[i - 1] or
                    register_numbs["func_code"].iloc[i] != register_numbs["func_code"].iloc[i - 1] or
                    register_numbs["reg_byte_len"].iloc[i] != register_numbs["reg_byte_len"].iloc[i - 1]):
                reg_cnt = (register_numbs["reg_num"].iloc[i - 1] - reg_numb) + 1
                attrs = {
                    "regCnt": str(reg_cnt),
                    "funcCode": str(register_numbs["func_code"].iloc[i - 1]),
                    "regNum": str(reg_numb),
                    "regOff": str(register_numbs["offset"].iloc[i - 1]),
                    "regByteLen": str(register_numbs["reg_byte_len"].iloc[i - 1])
                }
                SubElement(blocks, "block{}".format(block_number), attrs)
                reg_numb = register_numbs["reg_num"].iloc[i]
                block_number += 1
        reg_cnt = (register_numbs["reg_num"].iloc[-1] - reg_numb) + 1
        attrs = {
            "regCnt": str(reg_cnt),
            "funcCode": str(register_numbs["func_code"].iloc[-1]),
            "regNum": str(reg_numb),
            "regOff": str(register_numbs["offset"].iloc[-1]),
            "regByteLen": str(register_numbs["reg_byte_len"].iloc[-1])
        }
        SubElement(blocks, "block{}".format(block_number), attrs)

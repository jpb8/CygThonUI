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

    def create_array_excel(self):
        """
        Exports all the of Arrays and DEID for a supplied DTF
        :param array_file_name: Excel file name
        :param deid_file_name: Excel file name
        :return: None
        """
        data_groups = self.xml.find('dataGroups')
        arrs = {"id": [], "niceName": []}
        dg_elems = {"deid": [], "array_id": [], "tagName": [], "niceName": [], "desc": [], "dataType": []}
        for elem in data_groups:
            arrs["id"].append(elem.tag)
            arrs["niceName"].append(elem.get("niceName"))
            for died in elem.find("dgElements"):
                dg_elems["deid"].append(died.tag)
                dg_elems["array_id"].append(elem.tag)
                dg_elems["tagName"].append(died.get("tagname"))
                dg_elems["niceName"].append(died.get("niceName"))
                dg_elems["desc"].append(died.get("desc"))
                dg_elems["dataType"].append(died.get("type"))
        return self.template_export([arrs, dg_elems])

    def import_datagroups(self, data_elements, reg_gap):
        error_df = self._check_dg_excel_import(data_elements)
        data_elements.drop(data_elements.index[[tuple(error_df.index.values)]], inplace=True)
        data_groups_xml = self.data_groups
        data_groups = data_elements.data_group.unique()
        def_data_groups = self.def_data_groups
        for dg in data_groups:
            deids = data_elements.loc[data_elements["data_group"] == dg]
            dg_xml = DataGroup(dg, dg)
            dg_xml.add_deids(deids, reg_gap)
            data_groups_xml.append(dg_xml.xml)
            SubElement(def_data_groups, dg)
        self.save()
        error_df.fillna('None', inplace=True)
        return error_df.to_dict('records'), self.all_arrays()

    @staticmethod
    def _check_dg_excel_import(data_elements):
        reg_str_df = data_elements.loc[~data_elements['reg_num'].astype(str).str.isdigit()]
        reg_str_df["error"] = "reg_num must be integer"
        bit_str_df = data_elements.loc[~data_elements['bit'].astype(str).str.isdigit()]
        bit_str_df.dropna(subset=['bit'], inplace=True)
        bit_str_df["error"] = "bit must be integer"
        error_df = pd.concat([reg_str_df, bit_str_df])
        return error_df


class DataGroup:
    def __init__(self, name, nice_name):
        self.name = name
        self.nice_name = nice_name
        self.xml = self.create_datagroup_xml()

    def create_datagroup_xml(self):
        dg = etree.Element(self.name, {"niceName": self.nice_name, "devDG": "false", "baseOrd": "0",
                                       "canSend": "false", "canRecv": "true", "uccSend": "false", "uccRecv": "false"})
        SubElement(dg, "dgElements", {"byteOrder": "bigEndian", "secLev": "4"})
        SubElement(dg, "modbusReadBlocks")
        return dg

    def add_deids(self, deids, reg_gap):
        dg_elems = self.xml.find("dgElements")
        analog_df = deids[deids["dtype"] != "boolean"]
        digital_df = deids[deids["dtype"] == "boolean"]
        for i, deid in analog_df.iterrows():
            reg_num = deid.get("reg_num")
            desc = deid.get("description")
            dtype = deid.get("dtype")
            udc = deid.get("udc") if not pd.isna(deid.get("udc")) else None
            if udc:
                attrs = {"desc": desc, "udc": udc, "regNum": str(reg_num),
                         "type": dtype if dtype != "digital" else "ui2"}
            else:
                attrs = {"desc": desc, "regNum": str(reg_num), "type": dtype if dtype != "digital" else "ui2"}
            SubElement(dg_elems, "R{}".format(reg_num), attrs)
        self._add_digitals(dg_elems, digital_df)
        self._add_read_blocks(deids.reg_num.unique(), reg_gap)

    @staticmethod
    def _add_bits(dg_elems, ref):
        for i in range(0, 16):
            bit_str = "0{}".format(i) if i < 10 else str(i)
            attrs = {"desc": "Reg {} bit {}".format(ref, bit_str), "ref": ref, "bPos": str(i), "type": "Boolean"}
            SubElement(dg_elems, "{}B{}".format(ref, bit_str), attrs)

    @staticmethod
    def _add_digitals(dg_elems, digital_df):
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

    def _add_read_blocks(self, register_numbs, reg_gap):
        blocks = self.xml.find("modbusReadBlocks")
        block_number = 1
        register_numbs.sort()
        reg_numb = register_numbs[0]
        new = False
        for i in range(1, len(register_numbs)):
            if (register_numbs[i] - reg_gap) > register_numbs[i - 1]:
                reg_cnt = (register_numbs[i - 1] - reg_numb) + 1
                attrs = {
                    "regCnt": str(reg_cnt), "funcCode": "3", "regNum": str(reg_numb), "regOff": "-40001",
                    "regByteLen": "2"
                }
                SubElement(blocks, "block{}".format(block_number), attrs)
                reg_numb = register_numbs[i]
                block_number += 1
                new = True
            else:
                new = False
        if not new:
            reg_cnt = (register_numbs[-1] - reg_numb) + 1
            attrs = {
                "regCnt": str(reg_cnt), "funcCode": "3", "regNum": str(reg_numb), "regOff": "-40001",
                "regByteLen": "2"
            }
            SubElement(blocks, "block{}".format(block_number), attrs)

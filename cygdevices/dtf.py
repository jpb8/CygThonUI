from lxml.etree import SubElement
import pandas as pd

from .xml import XmlFile


class DTF(XmlFile):

    @property
    def data_groups(self):
        return self.xml.find("dataGroups")

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
        deid = self.xml.find("dataGroups/{}/dgElements/*[@tagname='{}']".format(array_name, tag))
        return deid.tag if deid is not None else False

    def get_analog_tag(self, array_name, deid):
        tag = self.xml.find("dataGroups/{}/dgElements/{}".format(array_name, deid))
        if tag is None:
            return None
        return tag.get("tagname")

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
        tag_name = parent_tag.get("tagname")
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

    def create_ai_deid(self, array_type, deid, tagname, data_type="r4"):
        dg_elem = self.xml.find('dataGroups/{}/dgElements'.format(array_type))
        SubElement(dg_elem, deid, {
            "niceName": tagname,
            "desc": tagname,
            "tagname": tagname,
            "type": data_type
        })

    def create_digital_deid(self, array_type, died, desc, ref, b_pos, data_type="bool"):
        pass

    def deid_tagname(self, array, deid):
        dg_elm = self.find_dg_element(array, deid)
        if dg_elm is None:
            return None
        return self.find_dg_element(array, deid).get("tagname")

    def create_array(self, name, nice_name):
        new_dg = SubElement(self.data_groups, name, {
            "niceName": nice_name,
            "udcCat": "UDCALL",
            "canSend": "false",
            "canRecv": "true",
            "uccSend": "false",
            "uccRecv": "true",
            "udcDefFac": "true",
            "devDG": "false",
            "baseOrd": "0",
            "maxCnt": "1"
        })
        return new_dg

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
        dg_elems = {"deid": [], "array_id": [], "tagName": [], "niceName": [], "desc": []}
        for elem in data_groups:
            arrs["id"].append(elem.tag)
            arrs["niceName"].append(elem.get("niceName"))
            for died in elem.find("dgElements"):
                dg_elems["deid"].append(died.tag)
                dg_elems["array_id"].append(elem.tag)
                dg_elems["tagName"].append(died.get("tagname"))
                dg_elems["niceName"].append(died.get("niceName"))
                dg_elems["desc"].append(died.get("desc"))
        return self.template_export([arrs, dg_elems])

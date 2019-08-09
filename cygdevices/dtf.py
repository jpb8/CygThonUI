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

    def create_array_excel(self, array_file_name, deid_file_name):
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
        df = pd.DataFrame(data=arrs)
        df2 = pd.DataFrame(data=dg_elems)
        df.to_excel(array_file_name)
        df2.to_excel(deid_file_name)
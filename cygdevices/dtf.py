from lxml import etree
from lxml.etree import SubElement
import pandas as pd


class DTF:
    # TODO : Create Parent class that parses supplied xml
    def __init__(self, dtf_filepath):
        self.xml = None
        self.device_xml_path = dtf_filepath
        self.create_xml()

    def create_xml(self):
        """
        Sets the xml prop to an ETREE root with the supplied xml file
        """
        tree = etree.parse(self.device_xml_path)
        root = tree.getroot()
        self.xml = root

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

    def get_discrete_deid(self, array_name, index, index2=None):
        pass

    def create_ai_deid(self, array_type, deid, index, reg, data_type="r4"):
        dg_elem = self.xml.find('dataGroups/{}/dgElements'.format(array_type))
        nice_name = "{} {}".format(index, reg)
        SubElement(dg_elem, deid, {
            "niceName": nice_name,
            "desc": nice_name,
            "tagname": "{}[{}]".format(index, reg),
            "type": data_type
        })

    def create_digital_deid(self, array_type, died, desc, ref, b_pos, data_type="bool"):
        pass

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

    def save(self, xml_file):
        file = open(xml_file, "wb")
        file.write(etree.tostring(self.xml, pretty_print=True))
        file.close()

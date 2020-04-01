from lxml import etree
import os
import pandas as pd
from io import BytesIO

class MasterComm:
    def __init__(self):
        self.root = etree.Element("DeviceDefinitions")

    @classmethod
    def template(cls):
        temp = {
            'id': ["TCP_DEV", "UPD_DEV"],
            'desc': ['TCP device Example', 'UPD device Example'],
            'ip': ['1.1.1.1', '255.255.255.255'],
            'port': ['502', '4131'],
            'commtype': ['TCP', 'UDP']
        }
        temp_df = pd.DataFrame(data=temp)
        sio = BytesIO()
        writer = pd.ExcelWriter(sio, engine="xlsxwriter")
        temp_df.to_excel(writer, sheet_name="Sheet1", index=False)
        writer.save()
        writer.close()
        sio.seek(0)
        return sio.getvalue()

    def append_comm_dev(self, dev_id, desc, ip, port, commtype="TCP"):
        comm_dev = CommDev(dev_id, desc, ip, port, commtype)
        self.root.append(comm_dev.xml)

    def import_devs(self, devs):
        devs = pd.read_excel(devs, sheet_name="Sheet1")
        for i, dev in devs.iterrows():
            if "ip" in dev and "port" in dev and "desc" in dev and "id" in dev and "commtype" in dev:
                self.append_comm_dev(
                    dev_id=dev.get("id"),
                    desc=dev.get("desc"),
                    ip=dev.get("ip"),
                    port=dev.get("port"),
                    commtype=dev.get("commtype")
                )

    def pretty_print(self):
        return etree.tostring(self.root, pretty_print=True)


class CommDev:
    def __init__(self, dev_id, desc, ip, port, commtype="TCP"):
        self.xml = None
        self.dev_id = dev_id
        self.desc = desc
        self.ip = ip
        self.port = port
        self.commtype = commtype.upper()
        self.create_xml()

    def create_xml(self):
        """
        Sets the xml prop to an ETREE root with the supplied xml file
        :return:
        """
        parser = etree.XMLParser(remove_blank_text=True)
        xml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils",
                                "{}_comm.xml".format(self.commtype.lower()))
        tree = etree.parse(xml_path, parser)
        root = tree.getroot()
        self.xml = root
        self.xml.set("device_id", self.dev_id)
        self.xml.find("DeviceAttributes/DeviceDescription").text = self.desc
        self.xml.find("DataGroups/DataGroup/DataGroupAttributes/Description").text = "Data Group for {}".format(
            self.dev_id)
        self.xml.find("DataGroups/DataGroup/DataGroupAttributes/FacilityId").text = self.dev_id
        if self.commtype == "TCP":
            self.xml.find("DeviceAttributes/ConfHistoryData/dgData/IP_Addr").text = self.ip
            self.xml.find("DeviceAttributes/ConfHistoryData/dgData/IP_Port").text = str(self.port)
        elif self.commtype == "UDP":
            self.xml.find("DeviceAttributes/ConfHistoryData/dgData/DestPort").text = str(self.port)
            self.xml.find("DeviceAttributes/ConfHistoryData/dgData/DestAddr").text = self.ip

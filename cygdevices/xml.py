from lxml import etree
from lxml.etree import SubElement
import pandas as pd
from io import BytesIO, StringIO
from backend.custom_azure import MEDIA_ACCOUNT_KEY

from azure.storage.blob.blockblobservice import BlockBlobService

from django.conf import settings


class XmlFile:
    def __init__(self, dtf_filepath):
        self.xml = None
        self.device_xml_path = dtf_filepath
        self.create_xml()

    def create_xml(self):
        """
        Sets the xml prop to an ETREE root with the supplied xml file
        """
        block_blob_service = BlockBlobService(account_name=settings.AZURE_ACCOUNT_NAME, account_key=MEDIA_ACCOUNT_KEY)
        file = block_blob_service.get_blob_to_bytes("media", self.device_xml_path)
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(BytesIO(file.content), parser)
        root = tree.getroot()
        self.xml = root

    @classmethod
    def template_export(cls, sheets):
        # TODO: Rename to build excel
        sio = BytesIO()
        writer = pd.ExcelWriter(sio, engine="xlsxwriter")
        for i, s in enumerate(sheets, start=1):
            df = pd.DataFrame(data=s)
            df.to_excel(writer, sheet_name="Sheet{}".format(i), index=False)
        writer.save()
        writer.close()
        sio.seek(0)
        return sio.getvalue()

    def pretty_print(self):
        return etree.tostring(self.xml, pretty_print=True)

    def save(self):
        output = StringIO()
        output = etree.tostring(self.xml, pretty_print=True)
        block_blob_service = BlockBlobService(account_name=settings.AZURE_ACCOUNT_NAME, account_key=MEDIA_ACCOUNT_KEY)
        block_blob_service.create_blob_from_text("media", self.device_xml_path, output)

    def delete(self):
        block_blob_service = BlockBlobService(account_name=settings.AZURE_ACCOUNT_NAME, account_key=MEDIA_ACCOUNT_KEY)
        block_blob_service.delete_blob("media", self.device_xml_path)

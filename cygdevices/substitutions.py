import pandas as pd
from lxml.etree import Element, SubElement
from lxml import etree
from io import BytesIO


class Substitutions:
    def __init__(self, excel, conds=None, actions=None):
        self.excel = excel
        self.conditions = pd.read_excel(excel, sheet_name="Conditions")
        self.actions = pd.read_excel(excel, sheet_name="Actions")
        self.act_headers = list(self.actions)
        self.cond_headers = list(self.conditions)
        self.sub_dict = {"Set": []}
        self.xml = self.build_xml()

    @staticmethod
    def build_xml():
        root = Element("Substitutions")
        SubElement(root, "Set", {"Label": "XML_Substitution"})
        return root

    @property
    def xml_set(self):
        return self.xml.find("Set")

    @classmethod
    def template(cls):
        conditions = {
            'ToolType': ["TextTool", "TextTool", "TextTool", "TextTool"],
            'Text': ['psi', 'bbl', 'f', 'api']
        }
        actions = {"Text": ['PSI', 'BBL', 'F', 'API']}
        cond_df = pd.DataFrame(data=conditions)
        actions_df = pd.DataFrame(data=actions)
        sio = BytesIO()
        writer = pd.ExcelWriter(sio, engine="xlsxwriter")
        cond_df.to_excel(writer, sheet_name="Conditions", index=False)
        actions_df.to_excel(writer, sheet_name="Actions", index=False)
        writer.save()
        writer.close()
        sio.seek(0)
        return sio.getvalue()

    def build_rules(self):
        # TODO: Build with lxml
        for index, row in self.conditions.iterrows():
            rule = SubElement(self.xml_set, "Rule")
            conditions = SubElement(rule, "Conditions")
            actions = SubElement(rule, "Actions")
            for cond in self.cond_headers:
                SubElement(conditions, cond).text = row[cond]
            for act in self.act_headers:
                SubElement(actions, act).text = self.actions.at[index, act]

    def pretty_print(self):
        return etree.tostring(self.xml, pretty_print=True)

import pandas as pd
from lxml.etree import Element, SubElement
from lxml import etree


class Substitutions:
    def __init__(self, excel, conds=None, actions=None):
        self.excel = excel
        self.conditions = pd.read_excel(excel, sheet_name="Conditions")
        self.actions = pd.read_excel(excel, sheet_name="Actions")
        self.act_headers = list(self.actions)
        self.cond_headers = list(self.conditions)
        self.sub_dict = {"Set": []}
        self.xml = Element("Set")

    def build_rules(self):
        # TODO: Build with lxml
        for index, row in self.conditions.iterrows():
            rule = SubElement(self.xml, "Rule")
            conditions = SubElement(rule, "Conditions")
            actions = SubElement(rule, "Actions")
            for cond in self.cond_headers:
                SubElement(conditions, cond).text = row[cond]
            for act in self.act_headers:
                SubElement(actions, act).text = self.actions.at[index, act]

    def pretty_print(self):
        return etree.tostring(self.xml, pretty_print=True)

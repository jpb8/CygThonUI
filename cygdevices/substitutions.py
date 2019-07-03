import pandas as pd

class Substitutions:
    def __init__(self, excel, conds=None, actions=None):
        self.excel = excel
        self.conditions = pd.read_excel(excel, sheet_name="Conditions")
        self.actions = pd.read_excel(excel, sheet_name="Actions")
        self.act_headers = list(self.actions)
        self.cond_headers = list(self.conditions)
        self.sub_dict = {"Set": []}

    def build_rules(self):
        # TODO: Build with lxml
        for index, row in self.conditions.iterrows():
            rule = {
                "Rule": {
                    "Conditions": {},
                    "Actions": {}
                }
            }
            for c in self.cond_headers:
                rule["Rule"]["Conditions"][c] = row[c]
            self.sub_dict["Set"].append(rule)
            for a in self.act_headers:
                rule["Rule"]["Actions"][a] = self.actions.at[index, a]

    def export_xml(self, filename="dict.xml"):
        self.build_rules()
        xml = dicttoxml(self.sub_dict, custom_root="Substitutions", attr_type=False, item_func=lambda x: None)
        xml = xml.decode()
        xml = xml.replace('<None>', '').replace('</None>', '')
        xmlfile = open(filename, "w")
        xmlfile.write(xml)
        xmlfile.close()

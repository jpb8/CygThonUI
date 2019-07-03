import pandas as pd
from .utils.abrvs import WORDS_UPPER
from io import BytesIO


class Points:
    def __init__(self, excel, sheet, df=None):
        self.excel = excel
        self.sheet = sheet
        self.df = pd.read_excel(excel, sheet_name=sheet)

    def update_point_desc(self, words=WORDS_UPPER):
        for index, row in self.df.iterrows():
            old_desc = str(row["longdescription"]).split(" ")
            new_desc = []
            for word in old_desc:
                new_desc.append(word) if word.upper() not in words else new_desc.append(words[word.upper()])
            long_desc = " ".join(new_desc)
            self.df.at[index, "newlongdesc"] = long_desc if len(new_desc) > 0 else ""
            self.df.at[index, "over80"] = 1 if len(long_desc) > 80 else None

    def update_alarms(self, alarm_config):
        for index, row in self.df.iterrows():
            udc = row["uniformdatacode"]
            if udc in alarm_config["digital"]:
                self.df.at[index, "alarm01priority"] = alarm_config["digital"][udc]
                self.df.at[index, "changed"] = True
            elif udc in alarm_config["analog"]:
                k, v = alarm_config["analog"][udc]
                self.df.at[index, k] = v
                self.df.at[index, "changed"] = True

    def export_to_excel(self, new_excel):
        self.df.to_excel(new_excel)

    def export(self):
        sio = BytesIO()
        writer = pd.ExcelWriter(sio, engine="xlsxwriter")
        self.df.to_excel(writer, sheet_name="NewLongDesc")
        writer.save()
        writer.close()
        sio.seek(0)
        return sio.getvalue()

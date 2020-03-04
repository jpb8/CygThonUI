import pandas as pd
from io import BytesIO
from django.utils.encoding import codecs


def no_commas(string):
    quotes = False
    output = ''
    for char in string:
        if char == '"' and not quotes:
            quotes = True
        elif char == '"' and quotes:
            quotes = False
        if quotes == False:
            output += char
        if char != ',' and quotes:
            output += char
        elif char == "," and quotes:
            output += "*"
    return output



def parse_scaling(df_scale, new):
    if len(new.columns) == 2:
        return df_scale
    attrs = []
    for col in new.columns:
        split = col.split(".")
        if len(split) > 1 and split[0] not in attrs:
            attrs.append(split[0])
    if len(attrs) < 1:
        new["attr"] = new[":Tagname"]
        new.columns = [":Tagname", "Area", "RawMin", "RawMax", "EngUnitsMin", "EngUnitsMax", "attr"]
        df_scale = df_scale.append(new, ignore_index=True, sort=False)
    else:
        rows = new.shape[0]
        for attr in attrs:
            if attr + ".RawMin" in new.columns and attr + ".EngUnitsMin" in new.columns:
                if attr + ".RawMin" not in new.columns:
                    cols = [":Tagname", "Area", attr + ".EngUnitsMin", attr + ".EngUnitsMax", attr + ".EngUnitsMin", attr + ".EngUnitsMax"]
                elif attr + ".EngUnitsMin" not in new.columns:
                    cols = [":Tagname", "Area", attr + ".RawMin", attr + ".RawMax", attr + ".RawMin", attr + ".RawMax"]
                else:
                    cols = [":Tagname", "Area", attr + ".RawMin", attr + ".RawMax", attr + ".EngUnitsMin", attr + ".EngUnitsMax"]
                temp = new[cols]
                temp["attr"] = [attr for i in range(rows)]
                temp.columns = [":Tagname", "Area", "RawMin", "RawMax", "EngUnitsMin", "EngUnitsMax", "attr"]
                df_scale = df_scale.append(temp, ignore_index=True, sort=False)
    return df_scale


def create_xlxs(templates):
    sio = BytesIO()
    writer = pd.ExcelWriter(sio, engine="xlsxwriter")
    df_scalers = pd.DataFrame(columns=[":Tagname", "Area", "RawMin", "RawMax", "EngUnitsMin", "EngUnitsMax", "attr"])
    for k, v in templates.items():
        df = pd.DataFrame([sub.split(",") for sub in v])
        df.columns = df.iloc[0]
        df = df[1:]
        reg_cols = [col for col in df if str(col).startswith('reg') or str(col).startswith('Reg')]
        bit_col = [col for col in df if str(col).startswith('bit') or str(col).startswith('Bit')]
        eng_units = [col for col in df if 'EngUnitsM' in str(col) or 'RawM' in str(col) or 'EngUnitsM' in str(col)]
        df_eng = df[list(df.columns[0:2]) + eng_units]
        df_scalers = parse_scaling(df_scalers, df_eng)
        source_col = [col for col in df if str(col).endswith('InputSource') or str(col).endswith('OutputDest')]
        df = df[list(df.columns[0:4]) + reg_cols + bit_col + source_col + eng_units]
        df.to_excel(writer, sheet_name=k, index=False)
    df_scalers.to_excel(writer, sheet_name="scales", index=False)
    writer.save()
    writer.close()
    sio.seek(0)
    return sio.getvalue()


def transform_galaxy(gal_file):
    templates = {}
    with codecs.EncodedFile(gal_file, 'utf-16-le') as f:
        while True:
            line = f.readline().decode('utf-16')
            if not line:
                break
            objs = []
            if line.startswith(":TEMPLATE="):
                template = line.split("=")[1].strip("\r\n")
                line = f.readline().decode('utf-16')
                while line != "\r\n" and line:
                    line = no_commas(line)
                    objs.append(line)
                    line = f.readline().decode('utf-16')
                if template not in templates:
                    templates[template] = objs
                else:
                    templates[template] = templates[template] + objs[1:]
    return create_xlxs(templates)

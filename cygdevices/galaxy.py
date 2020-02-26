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
        if char != ',' and quotes == True:
            output += char
        elif char == "," and quotes == True:
            output += "*"
    return output


def create_xlxs(templates):
    sio = BytesIO()
    writer = pd.ExcelWriter(sio, engine="xlsxwriter")
    for k, v in templates.items():
        df = pd.DataFrame([sub.split(",") for sub in v])
        df.columns = df.iloc[0]
        df = df[1:]
        reg_cols = [col for col in df if str(col).startswith('reg') or str(col).startswith('Reg')]
        bit_col = [col for col in df if str(col).startswith('bit') or str(col).startswith('Bit')]
        source_col = [col for col in df if str(col).endswith('InputSource') or str(col).endswith('OutputDest')]
        df = df[list(df.columns[0:4]) + reg_cols + bit_col + source_col]
        df.to_excel(writer, sheet_name=k, index=False)
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

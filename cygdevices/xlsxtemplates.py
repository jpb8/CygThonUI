from io import BytesIO
import pandas as pd


def template_export(sheets):
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

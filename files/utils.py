def handle_uploaded_file(f):
    with open('some/file/name.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def build_ajax_response_dict(data, header):
    rows = list(data[0].keys()) if len(data) > 0 else []
    response_data = {
        "rows": rows,
        "responseData": data,
        "header": header
    }
    return response_data
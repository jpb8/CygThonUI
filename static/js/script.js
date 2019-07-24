$(document).ready(function () {

    function createPointTable(points, rows) {
        var table = "<table style='width:100%'>" + buildHeaders(rows);
        for (i = 0; i < points.length; i++) {
            table += "<tr>";
            for (j = 0; j < rows.length; j++) {
                table += "<td style='font-size:8pt'>" + points[i][rows[j]] + "</td>";
            }
            table += "</tr>";
        }
        table += "</table>";
        return table
    }

    function buildHeaders(rows) {
        var headerHTML = "<tr>";
        for (i = 0; i < rows.length; i++) {
            headerHTML += "<th>" + rows[i] + "</th>";
        }
        headerHTML += "</tr>";
        return headerHTML
    }

    function createResponseHTML(data) {
        if (data.error) {
            return "<h1>ERROR</h1>"
        }
        var text = "<h2>" + data.header + "</h2>";
        var table = createPointTable(data.responseData, data.rows);
        text += table;
        return text
    }

    $("#dtf-died-check").submit(function (event) {
        event.preventDefault();
        var formData = $("#dtf-died-check").serialize();
        var _url = $(this).attr("action");
        var method = "POST";
        $(document.body).css({ 'cursor': 'wait' });
        $.ajax({
            url: _url,
            type: method,
            data: formData,
            success: function (data) {
                var text = createResponseHTML(data);
                $("#modal-body").html(text);
                $('#response-modal').modal('show');
            },
            error: function (request, error) {
                alert("Request: " + JSON.stringify(request));
            }
        });
        $(document.body).css({ 'cursor': 'default' });
    });

    $("#dds-mapping").submit(function (event) {
        event.preventDefault();
        var formData = new FormData($(this)[0]);
        var _url = $(this).attr("action");
        var method = "POST";
        $(document.body).css({ 'cursor': 'wait' });
        $.ajax({
            url: _url,
            type: method,
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
                var text = createResponseHTML(data);
                $("#modal-body").html(text);
                $('#response-modal').modal('show');
            },
            error: function (request, error) {
                alert("Request: " + JSON.stringify(request));
            }
        });
        $(document.body).css({ 'cursor': 'default' });
    });

    $("#dds-orphans").submit(function (event) {
        event.preventDefault();
        var formData = $("#dds-orphans").serialize();
        var _url = $(this).attr("action");
        var method = "POST";
        $(document.body).css({ 'cursor': 'wait' });
        $.ajax({
            url: _url,
            type: method,
            data: formData,
            success: function (data) {
                var text = createResponseHTML(data);
                $("#modal-body").html(text);
                $('#response-modal').modal('show');
            },
            error: function (request, error) {
                alert("Request: " + JSON.stringify(request));
            }
        });
        $(document.body).css({ 'cursor': 'default' });
    });

    $("#dds-facs").submit(function (event) {
        event.preventDefault();
        var formData = new FormData($(this)[0]);
        var _url = $(this).attr("action");
        var method = "POST";
        $(document.body).css({ 'cursor': 'wait' });
        $.ajax({
            url: _url,
            type: method,
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
                var text = createResponseHTML(data);
                $("#modal-body").html(text);
                $('#response-modal').modal('show');
            },
            error: function (request, error) {
                alert("Request: " + JSON.stringify(request));
            }
        });
        $(document.body).css({ 'cursor': 'default' });
    });

    $(".dds-util").click(function () {
        var _url = $(this).data("url");
        var _data = {id: $(this).data("id")};
        var method = "POST";
        $(document.body).css({ 'cursor': 'wait' });
        $.ajax({
            url: _url,
            type: method,
            data: _data,
            success: function (data) {
                var text = createResponseHTML(data);
                $("#modal-body").html(text);
                $('#response-modal').modal('show');
            },
            error: function (request, error) {
                alert("Request: " + JSON.stringify(request));
            }
        })
        $(document.body).css({ 'cursor': 'default' });
    });

    $("#map-unmapped").click(function () {
        var _url = $(this).data("url");
        var _data = {
            id: $(this).data("id"),
            map: $(this).data("map")
        };
        var method = "POST";
        $(document.body).css({ 'cursor': 'wait' })
        $.ajax({
            url: _url,
            type: method,
            data: _data,
            success: function (data) {
                var text = createResponseHTML(data);
                $("#modal-body").html(text);
                $("#device-info").html(data.devices_html);
                $('#response-modal').modal('show');
            },
            error: function (request, error) {
                alert("Request: " + JSON.stringify(request));
            }
        })
        $(document.body).css({ 'cursor': 'default' });
    });

    $(".dg-mappings").click(function () {
        var _url = $(this).data("url");
        var _data = {
            data_group: $(this).data("group"),
            device: $(this).data("device"),
            id: $(this).data("id")
        };
        var method = "POST";
        $(document.body).css({ 'cursor': 'wait' });
        $.ajax({
            url: _url,
            type: method,
            data: _data,
            success: function (data) {
                var text = createResponseHTML(data);
                $("#modal-body").html(text);
                $('#response-modal').modal('show');
            },
            error: function (request, error) {
                alert("Request: " + JSON.stringify(request));
            }
        })
        $(document.body).css({ 'cursor': 'default' });
    });

});
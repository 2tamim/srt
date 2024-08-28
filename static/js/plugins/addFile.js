var index_poc = 0;
function time_add_file_attach_poc() {
        var addresult = ""
        index_poc = index_poc + 1
        addresult += "<div id='time_add_input_div_poc_" + index_poc + "' class='display_none'>"
        addresult += "<input type='file' class='display_none multisteps-form__input form-control' id='time_add_input_poc_" + index_poc + "' name='time_add_input_poc_' style='background-color:#f3f4fc;'>"
        addresult += "</div>"
        $("#time_add_file_list_poc").append(addresult);


        $("input[type='file']").change(function (e) {
            var ifiles = e.target.files[0].name;
            addresult = "<div id='time_add_attachment_row_poc_" + index_poc + "' class='time_add_attachment_row'>"
            addresult += "<div class='width_80percent'>"
            addresult += ifiles
            addresult += "</div>"
            addresult += "<div class='width_10percent'>"
            addresult += "<img class='report_add_attachment_row_image' src='/static/img/icon/delete.svg' onclick='remove_time_attachment_element(" + index_poc + ")'>"
            addresult += "</div>"
            addresult += "</div>"
            $("#time_add_file_list").append(addresult)
        });
//        $("#time_add_input_poc_" + index_poc).trigger("click");

    }

var index_exploit = 0;
function time_add_file_attach_exploit() {
        var addresult = ""
        index_exploit = index_exploit + 1
        addresult += "<div id='time_add_input_div_exploit_" + index_exploit + "' class='display_none'>"
        addresult += "<input type='file' class='display_none multisteps-form__input form-control' id='time_add_input_exploit_" + index_exploit + "' name='time_add_input_exploit_' style='background-color:#f3f4fc;'>"
        addresult += "</div>"
        $("#time_add_file_list_exploit").append(addresult);


        $("input[type='file']").change(function (e) {
            var ifiles = e.target.files[0].name;
            addresult = "<div id='time_add_attachment_row_exploit_" + index_exploit + "' class='time_add_attachment_row'>"
            addresult += "<div class='width_80percent'>"
            addresult += ifiles
            addresult += "</div>"
            addresult += "<div class='width_10percent'>"
            addresult += "<img class='report_add_attachment_row_image' src='/static/img/icon/delete.svg' onclick='remove_time_attachment_element(" + index_exploit + ")'>"
            addresult += "</div>"
            addresult += "</div>"
            $("#time_add_file_list").append(addresult)
        });
        $("#time_add_input_exploit_" + index_exploit).trigger("click");

    }


// $(document).ready(function () {
//     $('input[type=radio]').change(function () {
//         alert("dsf");
//         // console.log('Radio button selected: ' + $(this).val());
//     });
// });

$(function () {
    var INDEX = 0;
    var message_response = ""
    var free_times = {};
    var product_state = false;
    var product = []
    $('#chat-input').keydown(function (event) {
        if (event.which === 13) {
            // Trigger your event here
            var msg = $("#chat-input").val();
            if (msg.trim() == '') {
                return false;
            }
            generate_message(msg, 'end');

            setTimeout(function () {
                sayToBot(msg);
            }, 500)
        }
    });

    $('#chatbot_btn').click(function () {
        $("#chatbot_btn").hide();
        $("#chatbot_panel").show();
    });

    $('#chatbot_close').click(function () {
        $("#chatbot_btn").show();
        $("#chatbot_panel").hide();
    });

    // $("input[type=radio][name='ello']").change(function () {
    //     // Code to execute when the radio button is selected
    //     alert("sdsf")
    // });

    $('input[type=radio][name="free_date"]').on('change', function () {
        console.log('Radio button selected: ' + $(this).val());
    });

    function sendmail(message) {
        $.ajax({
            type: "POST",
            url: 'sendmail',
            data: {
                name: message['name'],
                email: message['email'],
                number: message['number'],
                company: message['company'],
                content: message['content']
            },
            success: function (response) {
                console.log("message is sent.")
            }
        });
    }

    function utter_response(intent) {
        $.ajax({
            type: "POST",
            async: false,
            url: 'utter_response',
            data: {
                msg: intent
            },
            success: function (response) {
                if (response != null) {
                    message_response = response.res;
                    if (response.product.length != 0) {
                        product = response.product;
                        product_state = true;
                    }
                }
            }
        });
    }

    function free_timeslot() {
        $.ajax({
            type: "POST",
            async: false,
            url: 'free_timeslot',
            success: function (response) {
                if (response != null) {
                    free_times = response.res;
                    // console.log(response.res)
                }
            }
        });
    }

    function savelead(data) {
        $.ajax({
            type: "POST",
            // async: false,
            data: {
                name: data['name'],
                email: data['email'],
                number: data['number'],
                company: data['company'],
                file_id: data['file_id']
            },
            url: 'save_lead',
            success: function (response) {
                if (response != null) {
                    console.log(response.res)
                }
            }
        });
    }

    function session_register(user_msg, bot_msg, intent, confidence) {
        $.ajax({
            type: "POST",
            // async: false,
            url: 'session_register',
            data: {
                user_msg: user_msg,
                bot_msg: bot_msg,
                intent: intent,
                confidence: confidence
            },
            success: function (response) {
                console.log(response.res);
            }
        });
    }


    function sayToBot(message) {

        // $.ajax({
        //     type: "POST",
        //     url: 'spell_check',
        //     data: {
        //         msg: message
        //     },
        //     success: function (response) {
        //         message = response.res;
        //     }
        // });

        // $.ajax({
        //     // url: 'https://c12d42895ebb-15633984065905290001.ngrok-free.app/webhooks/rest/webhook',
        //     // url: 'https://cb81-83-234-227-10.ngrok-free.app/webhooks/rest/webhook',
        //     url: 'http://localhost:5005/webhooks/rest/webhook',
        //     type: 'POST',
        //     contentType: 'application/json',
        //     data: JSON.stringify({
        //         "message": message,
        //         "sender": "Sagar"
        //     }),
        //     success: function (data, textStatus) {
        //         if (data != null) {
        //             // generate_message(data, 'start');
        //             console.log(data)
        //         }
        //     },
        //     error: function (errorMessage) {
        //         msg = "Could not connect to server... :( Please try again.";
        //         // generate_message(msg, "user");
        //         // console.log("E")
        //         console.log('Error : ' + errorMessage);

        //     }
        // });

        $.ajax({
            // url: 'https://c12d42895ebb-15633984065905290001.ngrok-free.app/webhooks/rest/webhook',
            // url: 'https://cb81-83-234-227-10.ngrok-free.app/webhooks/rest/webhook',
            url: 'action_info',
            type: 'POST',
            data: {
                msg: message
            },
            success: function (data, textStatus) {
                if (data != null) {
                    console.log(data)
                    generate_message(data, 'start');
                }
            },
            error: function (errorMessage) {
                msg = "Could not connect to server... :( Please try again.";
                generate_message(msg, "user");
                console.log('Error : ' + errorMessage);

            }
        });
    }

    function generate_message(val, type) {
        INDEX++;
        var str = "";
        var msg = "";
        var buttons = "";
        var products = "";

        if (val.length < 1) {
            msg = "Could not connect to server... :( Please try again.";
        }
        else if (type == "self") {
            msg = val;
        }
        else if (typeof (val) == "string" && type == "end") {
            msg = val;
        }
        else {
            for (i = 0; i < val.length; i++) {
                if (val[i].hasOwnProperty("text")) {
                    msg += val[i].text + "<br>";
                }

                if (val[i].hasOwnProperty("buttons")) {
                    for (j = 0; j < val[i].buttons.length; j++) {
                        buttons += "<span class=\"block mr-2 mt-2\">";
                        buttons += "<button class=\"rounded-full shadow-sm shadow-sky-700 bg-white text-sm px-3 text-sky-500\">" + val[i].buttons[j].title + "</button>";
                        buttons += "</span>";
                    }
                }
                if (val[i].hasOwnProperty("image")) {
                    msg += "<img src='" + val[i].image + "' class='chat_img'>";
                }

                if (val[i].hasOwnProperty("custom")) {
                    if (val[i].custom.purpose == "message")
                        sendmail(val[i].custom.content);
                    // console.log(val[i].custom.content);
                    if (val[i].custom.purpose == "utter") {
                        console.log("val", val[i].custom.content);
                        utter_response(val[i].custom.content['intent']);
                        session_register(val[i].custom.content['text'], message_response, val[i].custom.content['intent'], val[i].custom.content['confidence'])
                        msg += message_response + "<br>";
                        if (product_state) {
                            product_state = false;
                            for (let i = 0; i < product.length; i++) {
                                const dict = product[i];
                                // Access the dictionary values using the keys

                                products += "<label>" + dict.name + "</label><br>";
                                products += "<label>" + dict.info + "</label><br>";
                                image_str = dict.file.split("\n");
                                for (let j = 0; j < image_str.length; j++) {
                                    products += "<img src='http://localhost:8000/static/product/" + dict.name + "/" + image_str[j] + "'><br>"
                                }
                            }
                        }

                    }
                    if (val[i].custom.purpose == "meeting") {
                        free_timeslot();
                        if (free_times.length >= 3)
                            free_times = free_times.slice(0, 3);
                        for (var i = 0; i < free_times.length; i++) {
                            msg += "<input type='radio' name='free_date' value='" + free_times[i]['start'] + "-" + free_times[i]['end'] + "' onchange='meet_book()'><label class='ms-4 font-serif'>" + free_times[i]['start'] + "-" + free_times[i]['end'] + "</label><br>"
                            msg += "<input type='text' value='" + val[i].custom.content['name'] + "' name='meeting_name' style='display: none'>"
                            msg += "<input type='text' value='" + val[i].custom.content['email'] + "' name='meeting_email' style='display: none'>"
                            msg += "<input type='text' value='" + val[i].custom.content['number'] + "' name='meeting_number' style='display: none'>"
                            msg += "<input type='text' value='" + val[i].custom.content['company'] + "' name='meeting_company' style='display: none'>"
                        }
                    }

                    if (val[i].custom.purpose == "lead") {
                        msg += val[i].custom.content["response"] + "<br>";
                        savelead(val[i].custom.content);
                    }
                }
            }
        }

        str += "<li class=\"flex flex-col justify-" + type + "\">";
        if (type == "end") {
            str += "<div class=\"ml-10 text-wrap break-all px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-tl-2xl rounded-br-2xl shadow-md shadow-gray-500/50\">";
        }
        else {
            str += "<div class=\"mr-10 relative px-4 py-2 text-sm text-white rounded-tr-2xl rounded-bl-2xl shadow-md shadow-sky-500/50 bg-sky-500\">";
        }
        str += msg;
        str += "<\/div><div class=\"flex flex-wrap\">";
        str += buttons;
        str += "</div><div>" + products
        str += "</div><\/li>";

        $("#chat-logs").append(str);
        if (type == 'end') {
            $("#chat-input").val('');
        }
        var scrollHeight = $('#chat-history')[0].scrollHeight;
        console.log(scrollHeight);
        $('#chat-history').scrollTop(scrollHeight);
    }

    $(document).delegate(".chat-btn", "click", function () {
        var value = $(this).attr("chat-value");
        var name = $(this).html();
        $("#chat-input").attr("disabled", false);
        generate_message(name, 'self');
    })

    $("#chat-circle").click(function () {
        $("#chat-circle").toggle('scale');
        $(".chat-box").toggle('scale');
    })

    $(".chat-box-toggle").click(function () {
        $("#chat-circle").toggle('scale');
        $(".chat-box").toggle('scale');
    })

})

function meet_book() {
    let selected_time = $('input[name="free_date"]:checked').val();
    $.ajax({
        type: "POST",
        // async: false,
        url: 'meeting_book',
        data: {
            time: selected_time,
            name: $("input[name=meeting_name]").val(),
            email: $("input[name=meeting_email]").val(),
            number: $("input[name=meeting_number]").val(),
            company: $("input[name=meeting_company]").val(),
        },
        success: function (response) {
            console.log(response.res);
        }
    });


}
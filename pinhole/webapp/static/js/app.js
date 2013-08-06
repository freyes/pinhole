App = Ember.Application.create({
    LOG_TRANSITIONS: true
});

filepicker.setKey("A4glBC8jYTROreKupl7SXz");

function upload_dialog() {

    console.log("upload!");
    filepicker.pickMultiple({mimetype:"image/*",
                             location: "S3"},
                            function(InkBlobs){
                                $.each(InkBlobs, function(index, item) {
                                    console.log("Storing: " + item.filename);
                                    filepicker.store(item, function(InkBlob) {
                                        console.log("Saving " + InkBlob.filename);
                                        var r = App.UploadedPhoto.createRecord(InkBlob);
                                        r.save();
                                    },
                                                     function(FPError){
                                                         console.log(FPError.toString());
                                                     },
                                                    function(progress) {
                                                        console.log("Loading: "+progress+"%");
                                                    });
                                });
                            });
}

function getView(name) {
    var template = '';
    $.ajax(
        {
            url: '/medis/templates/' + name + '.html',
            async: false,
            success: function (text) {
                template = text;
            }
        });
    return Ember.Handlebars.compile(template);
};

function isAuthenticated() {
    var result = null;

    $.ajax("/api/v1/authenticated",
           {async: false,
            success: function(data, textStatus, jqXHR) {
                result = data;
            }
           });
    if (result != null && result["authenticated"] == true)
        return result;
    else
        return null;
};


function do_login(frm) {
    console.log(frm);
    $(frm).addClass("disabled");
    $(frm).find("#btn_submit").addClass("disabled").html('<i class="icon-spinner icon-spin icon-large"></i>');
    var username = $(frm).find("#username").val();
    var password = $(frm).find("#password").val();

    $.ajax("/api/v1/authenticated",
           {type: "POST",
            data: {username: username, password: password},
            success: function(data, textStatus, jqXHR) {
                console.log(data);
                App.__container__.lookup("controller:index").transitionToRoute("index");
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(errorThrown);
                var response = $.parseJSON(jqXHR.responseText);
                $(frm).find("#btn_submit").removeClass("disabled").html("Sign in");
                $("#div_login_alert").html(response["message"]).removeClass("hide");
            }
           });

    return false;
};

jQuery.validator.setDefaults({
    errorPlacement: function(error, element) {
        var e;
        if(element.parent().hasClass('input-prepend') || element.parent().hasClass('input-append') || element.parent().hasClass('checkbox')) {
            e = element.parent();
        } else {
            e = element;
        }
        if (e.next().length > 0)
            e.next().replaceWith(error);
        else
            error.insertAfter(e);
    },
    highlight: function(element) {
        console.log("Adding error");
        console.log($(element).closest('.control-group'));
        $(element).closest('.control-group').removeClass("success").addClass('error');
    },
    success: function(element) {
        $(element).removeClass("error").closest('.control-group').removeClass('error').addClass("success");
        if (!$(element).prev().hasClass("checkbox"))
            $(element).addClass("icon-ok");
    }
});

Ember.Handlebars.registerBoundHelper('date', function(date) {
  return moment(date).fromNow();
});

Ember.Handlebars.registerBoundHelper('datetime', function(datetime) {
  return moment(datetime).fromNow();
});

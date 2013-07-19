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

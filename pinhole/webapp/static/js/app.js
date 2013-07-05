App = Ember.Application.create();

filepicker.setKey("A4glBC8jYTROreKupl7SXz");

function upload_dialog() {

    console.log("upload!");
    filepicker.pickAndStore({mimetype:"image/*"},
                            {location:"S3"}, function(InkBlobs){
                                console.log(JSON.stringify(InkBlobs));
                            });
}

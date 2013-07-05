App = Ember.Application.create();

filepicker.setKey("A4glBC8jYTROreKupl7SXz");

function upload_dialog() {

    console.log("upload!");
    filepicker.pickAndStore({mimetype:"image/*"},
                            {location:"S3"}, function(InkBlobs){
                                $.each(InkBlobs, function(index, item) {
                                    console.log(item);
                                    var r = App.UploadedPhoto.createRecord(item);
                                    r.save();
                                });
                            });
}

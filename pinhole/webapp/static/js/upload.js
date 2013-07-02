$.ready(function() {
    filepicker.setKey("A4glBC8jYTROreKupl7SXz");

    $(".upload").click(function() {
        console.log(this);
        filepicker.pickAndStore({mimetype:"image/*"},
                                {location:"S3"}, function(InkBlobs){
                                    console.log(JSON.stringify(InkBlobs));
                                });
    });
};
App.UploadedPhoto = DS.Model.extend({
    url: DS.attr('string'),
    filename: DS.attr('string'),
    size: DS.attr('string'),
    key: DS.attr("string"),
    isWriteable: DS.attr("string")
});

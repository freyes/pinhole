App.UploadedPhoto = DS.Model.extend({
    url: DS.attr('string'),
    filename: DS.attr('string'),
    size: DS.attr('number'),
    key: DS.attr("string"),
    isWriteable: DS.attr("boolean")
});

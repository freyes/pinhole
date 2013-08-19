App.UploadedPhoto = DS.Model.extend({
    url: DS.attr('string'),
    filename: DS.attr('string'),
    size: DS.attr('number'),
    key: DS.attr("string"),
    isWriteable: DS.attr("boolean")
});

App.User = DS.Model.extend({
    username: DS.attr("string"),
    email: DS.attr("string"),
    firstName: DS.attr("string"),
    lastName: DS.attr("string"),
    active: DS.attr("boolean"),
    fullName: function() {
        return this.get('firstName') + ' ' + this.get('lastName');
    }.property()
});

App.Photo = DS.Model.extend({
    title: DS.attr("string"),
    description: DS.attr("string"),
    timestamp: DS.attr("string"),
    //roll: DS.attr(),
    public: DS.attr("boolean"),
    rating: DS.attr("number"),
    //tags: DS.attr("string"),
    height: DS.attr("number"),
    width: DS.attr("number"),
    make: DS.attr("string"),
    model: DS.attr("string"),
    software: DS.attr("string"),
    dateTime: DS.attr("string"),
    dateTimeDigitized: DS.attr("string"),
    dateTimeOriginal: DS.attr("string"),
    // calculated properties
    orientation: function() {
        return this.get("height") < this.get("width") ? "landscape" : "portrait";
    },
    isPortrait: function () {
        return this.get("height") > this.get("width");
    },
    thumbnail: function() {
        return "/api/v1/photos/file/" + this.get("id") + "/thumbnail/f.jpg";
    }.property(),
    small_240: function() {
        return "/api/v1/photos/file/" + this.get("id") + "/small_240/f.jpg";
    }.property(),
    small_320: function() {
        return "/api/v1/photos/file/" + this.get("id") + "/small_320/f.jpg";
    }.property(),
    large_1024: function() {
        return "/api/v1/photos/file/" + this.get("id") + "/large_1024/f.jpg";
    }.property()
});

App.NewUser = Ember.Object.extend({
    
});
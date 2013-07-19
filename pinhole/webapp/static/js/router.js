App.Router.map(function() {
    // put your routes here
    this.route("upload", { path: "/upload" });
    this.route("about", {path: "/about"});
    this.resource("photos", function() {
        this.route("view", {path: "/:photo_id"});
    });
});

App.IndexRoute = Ember.Route.extend({
  setupController: function(controller){
      controller.set("content", App.Photo.find());
  }
});

App.UploadRoute = Ember.Route.extend({
    model: function() {
        return App.UploadedPhoto.find();
    }
});

App.UserRoute = Ember.Route.extend({
    model: function() {
        return App.User.find();
    }
});

App.PhotosViewRoute = Ember.Route.extend({
    // renderTemplate: function() {
    //     debugger;
    //     this.render("photos.view");
    // },
    model: function(params) {
        return App.Photo.find(params.photo_id);
    }
});

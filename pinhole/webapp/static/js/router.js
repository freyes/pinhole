App.Router.map(function() {
  // put your routes here
    this.route("upload", { path: "/upload" });
    this.route("about", {path: "/about"});
});

App.IndexRoute = Ember.Route.extend({
  model: function() {
    return ['red', 'yellow', 'blue'];
  }
});

App.UploadRoute = Ember.Route.extend({
    model: function() {
        return App.UploadedPhoto.find();
    }
});

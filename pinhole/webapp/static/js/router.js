App.Router.map(function() {
    // put your routes here
    this.route("about", {path: "/about"});
    this.resource("photos", function() {
        this.route("view", {path: "/:photo_id"});
        this.route("upload", { path: "/upload" });
        this.route("share", { path: "/share" });
    });
    this.route("loggedOut", {path: "/loggedOut"});
    this.route("login", {path: "/login"});
    this.route("logout", {path: "/logout"});
    this.route("password_reset", {path: "/password_reset"});
    this.route("register_account", {path: "/register"});
    this.route("register_account_done", {path: "/register_done"});
});

App.IndexRoute = Ember.Route.extend({
    redirect: function() {
        var authenticated = isAuthenticated();
        if (!authenticated) {
            this.transitionTo("login");
        }
    },
    setupController: function(controller) {
        controller.set("content", App.Photo.find({limit: 5,
                                                  order_by: "-timestamp"}));
    }
});

App.UserRoute = Ember.Route.extend({
    model: function() {
        return App.User.find();
    }
});

App.PhotosIndexRoute = Ember.Route.extend({
    setupController: function(controller){
        controller.set("content", App.Photo.find({order_by: "-timestamp"}));
    }
});

App.PhotosViewRoute = Ember.Route.extend({
    model: function(params) {
        return App.Photo.find(params.photo_id);
    }
});

App.PhotosUploadRoute = Ember.Route.extend({
    model: function() {
        return App.UploadedPhoto.find();
    }
});

App.LogoutRoute = Ember.Route.extend({
    renderTemplate: function(controller, model) {
        try {
            controller.logout();
            this._super(controller, model);
        } catch (e) {
            console.log(e);
        }
    }
});

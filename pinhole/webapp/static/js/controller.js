App.ApplicationController = Ember.Controller.extend({
    user: function() {
        return App.User.find();
    }
});

App.CurrentUserController = Ember.ObjectController.extend({
    isSignedIn: function() {
        console.log("computing currentUser.isSignedIn");
        return (this.get("content") != null);
    }.property("@content").readOnly()
});

// Create the login controller
App.LoginController = Ember.ObjectController.extend({
    username: '',
    password: '',
    isError: false,
    errorMessage: "",
    tryLogin: function() {
        var controller = this;

        $.ajax("/api/v1/authenticated",
               {type: "POST",
                data: {username: this.get("username"), 
                       password: this.get("password")},
                success: function(data, textStatus, jqXHR) {
                    console.log(data);
                    controller.set("isError", false);
                    controller.set("errorMessage", "");

                    var store = controller.get("store");
                    var object = store.load(App.User, data["user"]);
                    var user = App.User.find(object.id);
                    var container = controller.get("container");
                    container.lookup('controller:currentUser').set('content', user);
                    container.typeInjection('controller', 'currentUser', 'controller:currentUser');

                    controller.transitionToRoute("index");
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    console.log(errorThrown);

                    var response = $.parseJSON(jqXHR.responseText);
                    this.set("errorMessage", response["message"]);
                    this.set('isError', true);
                }
               });
    }
});

App.LogoutController = Ember.ObjectController.extend({
    loggedOut: false,
    isError: false,
    errorMessage: "",
    logout: function() {
        var controller = this;
        $.ajax("/api/v1/authenticated",
               {
                   type: "delete",
                   success: function(data) {
                       controller.set("loggedOut", true);
                       console.log("success");
                       var container = controller.get("container");
                       container.lookup('controller:currentUser').set('content', {});
                       controller.transitionTo("index");
                   },
                   error: function(jqXHR, textStatus, errorThrown) {
                       console.log("error");
                       var response = $.parseJSON(jqXHR.responseText);
                       controller.set("errorMessage", response["message"] || textStatus);
                       controller.set("isError", true);
                   }
               });
        console.log("logging out");
    }
});

Ember.Application.initializer({
  name: "currentUser",
  initialize: function(container, application) {
    store = container.lookup('store:main');
    var authenticated = isAuthenticated();
    if (authenticated) {
        var object = store.load(App.User, authenticated["user"]);
        var user = App.User.find(object.id);
        controller = container.lookup('controller:currentUser').set('content', user);
        container.typeInjection('controller', 'currentUser', 'controller:currentUser');
    }
  }
});

App.PhotosIndexController = Ember.ArrayController.extend({
    sortAscending: false,
    sortProperties: ['id'],
    actions: {
        edit: function() {
            console.log("meh");
        }
    }
});

App.PhotosViewController = Ember.ObjectController.extend({
    isEditing: false,
    edit: function() {
        this.set("isEditing", true);
    },
    acceptChanges: function() {
        this.set("isEditing", false);
        if(this.get('model').get('isSaving')) return;
        this.get("model").save();
    },
    cancelChanges: function() {
        this.set("isEditing", false);
        this.get("model").reload();
    },
    newTag: function(name) {
        var model = this.get("model");
        $.ajax("/api/v1/photos/" + model.id + "/tags",
               {
                   type: "POST",
                   data: {name: name},
                   success:  function(data, textStatus, jqXHR) {
                       model.reload();
                   },
                   error: function(jqXHR, textStatus, errorThrown) {
                       console.log(jqXHR.responseText);
                   }
               });
    }
});

App.RegisterAccountController = Ember.ObjectController.extend({
    needs: ["register_account_done"],
    content: {}
});

App.RegisterAccountDoneController = Ember.ObjectController.extend({
    needs: ["register_account", "login"],
    account_created: function() {
        return this.get("controllers.register_account").get("account_created");
    }.property("controllers.register_account.account_created")
});

App.UserWidgetController = Ember.ObjectController.extend({
    isSignedIn: function() {
        console.log("computing isSignedIn");
        var c = this.get("currentUser");
        if (!c)
            return false;

        return c.get("isSignedIn");
    }.property("controllers.currentUser.content")
});

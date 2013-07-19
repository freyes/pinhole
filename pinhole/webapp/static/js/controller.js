App.ApplicationController = Ember.Controller.extend({
    user: function() {
        return App.User.find();
    }
});
grrr = null;
App.CurrentUserController = Ember.ObjectController.extend({
    isSignedIn: function() {
        return (this.get("content") != null);
    }.property("@content")
});

// Create the login controller
App.loginController = Ember.Object.create({
    username: '',
    password: '',
    isError: false,

    tryLogin: function() {
        // Simulate server delay
        Ember.run.later(this, this._serverLogin, 100);
    },
    _serverLogin: function() {
        // Normally this would go to the server. Simulate that.
        if(this.get('username') === "test" &&
           this.get('password') === "test") {
            this.set('isError', false);
            this.set('username', '');
            this.set('password', '');
            App.stateManager.send('loginSuccess');
        } else {
            this.set('isError', true);
            App.stateManager.send('loginFail');
        }
    }
});

Ember.Application.initializer({
  name: "currentUser",
  initialize: function(container, application) {
    store = container.lookup('store:main');
    var authenticated = isAuthenticated();
    if (authenticated) {
        object = store.load(App.User, authenticated["user"]);
        user = App.User.find(object.id);
        controller = container.lookup('controller:currentUser').set('content', user);
        container.typeInjection('controller', 'currentUser', 'controller:currentUser');
    }
  }
});

App.IndexController = Ember.ArrayController.extend({
    sortAscending: true,
    sortProperties: ['id']
});

App.ImgView = Ember.View.extend({
    tagName: 'img',
    attributeBindings: ['src'],
    src: ""
});

App.RegisterFormView = Ember.View.extend({
    tagName: "form",
    classNames: ['register'],
    classNameBindings: ['isEnabled::disabled'],
    isEnabled: true,
    didInsertElement: function() {
        var frm = $("#" + this.elementId);
        frm.validate({
            messages: {
                username: {
                    required: "Please enter a valid username",
                    remote: "The"
                },
                password_2: {
                    equalTo: "Your passwords don't match",
                    required: "Please repeat your password"
                },
                tos: {
                    required: "To use this service you have to accept the terms of use"
                }
            },
            rules: {
                username: {
                    required: true,
                    minlength: 4,
                    remote: {
                        url: "/api/v1/users_available",
                        type: "post",
                        contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
                        cache: false
                    }
                },
                email: {
                    required: true,
                    email: true,
                    remote: {
                        url: "/api/v1/users_available",
                        type: "post",
                        contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
                        cache: false
                    }
                },
                password_1: {
                    required: true,
                    minlength: 8
                },
                password_2: {
                    equalTo: "#password_1",
                    minlength: 8,
                    required: true
                },
                tos: {
                    required: true
                }
            }
        });
    },
    submit: function(event) {
        console.log("Starting submit handler");
        var frm = $("#" + this.elementId);
        //frm.append("<i class='icon-spinner icon-spin'></i>");
        frm.append("swa");

        if (!frm.valid()) {
            console.log("form is not in a valid state");
            return false;
        }

        console.log("getting controller");
        var controller = this.get("controller");
        // TODO: lock the form while the call is being processed
        try {
            var new_user = {username: frm.find("input#username").val(),
                            email: frm.find("input#email").val(),
                            password: frm.find("input#password_1").val()};
            console.log("register info");
            console.log(new_user);
            $.ajax({
                url: "/api/v1/users",
                dataType: "json",
                type: "POST",
                data: new_user,
                success: function(data) {
                    console.log(JSON.stringify(data));
                    controller.set("account_created", true);
                    controller.transitionToRoute("register_account_done");
                    // we indicate to the app that we are logged in
                    var object = store.load(App.User, data["user"]);
                    var user = App.User.find(object.id);
                    var container = controller.get("container");
                    container.lookup('controller:currentUser').set('content', user);
                    container.typeInjection('controller', 'currentUser', 'controller:currentUser');
                    console.log("injected current user");
                },
                error: function(jqXHR, textStatus, errorThrown){
                    console.log(errorThrown);
                    frm.append(errorThrown);
                },
                complete: function() {
                    console.log("Ajax call completed");
                    frm.addClass("register-done");
                }
            });

        } catch (e) {
            console.log(e);
        }
        return false;
    }
});

App.LoginFormView = Ember.View.extend({
    tagName: "form",
    classNames: ['login'],
    didInsertElement: function() {
        var frm = $("#" + this.elementId);
        frm.validate({
            rules: {
                username: {required: true},
                password: {required: true}
            }
        });
    },
    submit: function(event) {
        event.preventDefault();
        event.stopPropagation();
        var frm = $("#" + this.elementId);

        if (!frm.valid())
            return;

        this.get("controller").tryLogin();
    }
});


App.UserWidgetView = Ember.View.extend({
    needs: ["currentUser"],
    tagName: "ul",
    classNames: ["nav", "pull-right"],
    classNameBindings: ['isSignedIn::hide'],
    isSignedIn: function() {
        console.log("computing isSignedIn");
        var c = this.get("controller");
        if (!c)
            return false;
        c = c.get("currentUser");
        if (!c)
            return false;

        return c.get("isSignedIn");
    }.property("controllers.currentUser")
});


// App.PhotosViewView = Ember.View.extend({
// });

App.EditTextView = Ember.TextField.extend({
    didInsertElement: function () {
        this.$().focus();
    },
    focusOut: function() {
        this.get("controller").send("acceptChanges");
    },
    insertNewline: function() {
        this.get("controller").send("acceptChanges");
    },
    cancel: function() {
        this.get("controller").send("cancelChanges");
    }
});

Ember.Handlebars.helper('edit-text', App.EditTextView);

App.EditTagView = Ember.TextField.extend({
    classNames: ['edit'],
    valueBinding: 'tag.name',
    change: function () {
        var value = this.get('value');
        if (Ember.isEmpty(value)) {
            this.get('controller').removeTodo();
        }
    },
    focusOut: function () {
        this.set('controller.isEditing', false);
    },
    insertNewline: function () {
        this.set('controller.isEditing', false);
    },
    didInsertElement: function () {
        this.$().focus();
    }
});


App.NewTagView = Ember.TextField.extend({
    photo: null,
    didInsertElement: function () {
        this.$().focus();
    },
    acceptChanges: function() {
        var name = this.get("value");
        if (!name)
            return;

        this.get('controller').send('newTag', name);
        this.set("value");
    },
    focusOut: function() {
        this.acceptChanges();
    },
    insertNewline: function() {
        this.acceptChanges();
    },
    cancel: function() {
        this.set("value", "");
    }
});

Ember.Handlebars.helper('new-tag', App.NewTagView);

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
        var frm = $("#" + this.elementId);
        frm.append("<i class='icon-spinner'></i>");

        if (!frm.valid()) {
            console.log("form is not in a valid state");
            return false;
        }

        // TODO: lock the form while the call is being processed
        try {
            var new_user = {username: frm.find("input#username").val(),
                            email: frm.find("input#email").val(),
                            password: frm.find("input#password_1").val()};
            $.ajax({
                url: "/api/v1/users",
                dataType: "json",
                type: "POST",
                data: new_user,
                success: function(data) {
                    console.log(data);
                    frm.append("account created");
                },
                error: function(jqXHR, textStatus, errorThrown){
                    console.log(errorThrown);
                    frm.append(errorThrown);
                },
                complete: function() {
                    frm.addClass("register-done");
                }
            });

        } catch (e) {
            console.log(e);
        }
        return false;
    }
});

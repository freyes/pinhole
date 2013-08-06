var page = require('webpage').create();
var server = require('webserver').create();
var system = require('system');
var fs = require('fs');
var host, port = 8081;
var fport = system.env.PORT;
if (!fport)
    fport = "8082";

console.log("Using port " + fport);

var baseurl = "http://localhost:" + fport;

var casper = require('casper').create({
    logLevel: "debug"
});

casper.on('remote.message', function(message) {
    console.log(message);
});


var listening = server.listen(port, function (request, response) {
    //console.log("Requested "+request.url);
    
    var filename = ("pinhole/webapp/" + request.url.slice(1)).replace(/[\\\/]/g, fs.separator);
    
    if (!fs.exists(filename) || !fs.isFile(filename)) {
        response.statusCode = 404;
        response.write("<html><head></head><body><h1>File Not Found</h1><h2>File:"+filename+"</h2></body></html>");
        response.close();
        return;
    }

    // we set the headers here
    response.statusCode = 200;
    response.headers = {"Cache": "no-cache", "Content-Type": "text/html"};
   
    response.write(fs.read(filename));
    
    response.close();
});
if (!listening) {
    console.log("could not create web server listening on port " + port);
    phantom.exit(1);
}

page.onConsoleMessage = function(msg, line, source) {
   console.log(msg);
}

casper.test.begin("Test load index", 1, function(test) {
    casper.start(baseurl + "/media/index.html", function() {
        test.assertTitle("Pinhole");
    });

  casper.run(function() {
      test.done();
  });
});


casper.test.begin("Test register", 1, function(test) {
    casper.viewport(1280, 800);
    casper.start(baseurl + "/media/index.html", function() {
        test.assertTitle("Pinhole");
    });

    casper.then(function() {
        this.echo("Clicking register now");
        this.clickLabel("Register now!", "a");
    });

    casper.waitFor(function() {
        return this.evaluate(function() {
            return ($("form.register").length > 0);
        });
    });

    casper.then(function() {
        this.fill("form.register", {
            username: "foobar",
            password_1: "12345678",
            password_2: "12345678",
            email: "foobar@example.com",
            tos: true
        }, false);
    });

    casper.waitFor(function check() {
        return this.evaluate(function() {
            return $("form.register").valid();
        });
    }, function then() {
        this.echo("The form is valid, we are going to submit it");
        this.echo("Capturing screenshot 0");
        this.capture("../pinhole/webapp/static/foo0.png");
        this.click({type: "xpath", path: "//*[@value='Submit']"});
    });

    casper.waitFor(function check() {
        return this.evaluate(function() {
            return (document.body.innerText.indexOf("Welcome to Pinhole") != -1);
            //return /\/register_done$/.test(String(window.location));
        });
    }, function then() {
        this.evaluateOrDie(function() {
            return (document.body.innerText.indexOf("Welcome to Pinhole") != -1);
        }, "not found 'Welcome to pinhole'");
    }, function timeout() {
        this.capture("../pinhole/webapp/static/foo2.png");
        this.evaluate(function() {
            console.log(window.location);
        });
        this.echo("browser wasn't redirected to '/register_done'");
        casper.exit(1);
    }, 5000);

    casper.then(function() {
        this.evaluate(function() {
            $("a.btn-success").click();
        });
    });

    casper.waitFor(function check() {
        return this.evaluate(function (){
            return ($('*:contains("Hi, foobar")').length > 0);
        });
    }, function then() {
        this.echo("welcome message found");
    }, function timeout() {
        this.capture("../pinhole/webapp/static/foo3.png");
        this.echo("index message not found");
        casper.exit(1);
    }, 5000);

  casper.run(function() {
      test.done();
      this.echo("Done.").exit(0);
  });
});

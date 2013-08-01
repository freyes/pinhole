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
        this.echo("Capturing screenshot 0");
        this.capture("../pinhole/webapp/static/foo0.png");
        this.evaluate(function() {
            $('form.register').submit();
        });
        this.capture("../pinhole/webapp/static/foo01.png");
    }).waitFor(function check() {
        this.echo("waitfor");
        this.capture("../pinhole/webapp/static/foo02.png");
        return this.evaluate(function() {
            return (document.body.innerText.indexOf("account created") != -1);
            //return $("form.register").hasClass("done");
        });
    }, function then() {
        this.echo("Capturing screenshot 1");
        this.capture("../pinhole/webapp/static/foo1.png");
        this.evaluateOrDie(function() {
            return (document.body.innerText.indexOf("account created") != -1);
        }, "not found 'account created'");
    }, function timeout() {
        this.capture("../pinhole/webapp/static/foo2.png");
        this.echo("form didn't get 'done' class");
        casper.exit(1);
    }, 15000);

  casper.run(function() {
      test.done();
  });
});

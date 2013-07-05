requirejs.config({
  baseUrl: '/media/js',

  paths: {
      jquery: 'vendor/jquery-1.9.1.min',
      app: 'app/index',
      setup: "lib/setup",
      jqueryfy: "vendor/jqueryify",
      json2ify: "vendor/json2ify",
      spine: "vendor/spine",
      "lib/setup": "app/lib/setup",
      "es5-shimify": "vendor/es5-shimify"
  },

  shim: {
  }
});

require(['app'],

function(App) {
    //window.bTask = new App();
});

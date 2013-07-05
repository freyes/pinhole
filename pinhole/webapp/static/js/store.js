App.Store = DS.Store.extend({
});


DS.RESTAdapter.reopen({
  namespace: 'api/v1'
});

app = angular.module 'find.a.slot'

app.controller 'HomeCtrl', ['Datastore', 'venues', class HomeCtrl

  Datastore = null

  constructor: (_Datastore, @venues) ->
    Datastore = _Datastore
    @venues = @venues.data.data

]

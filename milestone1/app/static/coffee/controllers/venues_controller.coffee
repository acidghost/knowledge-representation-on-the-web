app = angular.module 'find.a.slot'

app.controller 'VenuesCtrl', ['Datastore', 'venues', class VenuesCtrl

  Datastore = null

  constructor: (_Datastore, @venues) ->
    Datastore = _Datastore
    @venues = @venues.data.data

  show_venue: (venue) ->
    console.log venue

]

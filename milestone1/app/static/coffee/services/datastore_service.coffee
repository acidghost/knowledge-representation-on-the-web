app = angular.module 'find.a.slot'

app.factory 'Datastore', ['$http', ($http) ->

  venues: (name) ->
    params = {}
    params.name = name if name
    $http
      method: 'get'
      url: '/venues'
      params: params

]

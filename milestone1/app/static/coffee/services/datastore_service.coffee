app = angular.module 'find.a.slot'

app.factory 'Datastore', ['$http', ($http) ->

  venues: (uri) ->
    url = "/venues#{if uri? then '/'+uri else ''}"
    $http.get url

]

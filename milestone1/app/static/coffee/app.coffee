app = angular.module 'find.a.slot', [
  'ui.bootstrap',
  'ui.router'
]

app.config ['$stateProvider', '$urlRouterProvider', ($stateProvider, $urlRouterProvider) ->

  $urlRouterProvider.otherwise '/home'

  $stateProvider
    .state 'home',
      url: '/home'
      templateUrl: 'static/templates/index.html'
      controllerAs: 'home'
      controller: 'HomeCtrl'
      resolve:
        venues: ['Datastore', (Datastore) ->
          Datastore.venues()
        ]

]

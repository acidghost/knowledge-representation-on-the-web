app = angular.module 'find.a.slot', [
  'ui.bootstrap',
  'ui.router'
]

app.config ['$stateProvider', '$urlRouterProvider', ($stateProvider, $urlRouterProvider) ->

  $urlRouterProvider.otherwise '/'

  $stateProvider
    .state 'index',
      url: ''
      templateUrl: 'static/templates/index.html'

]

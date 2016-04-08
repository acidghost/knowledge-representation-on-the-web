app = angular.module 'find.a.slot', [
  'ui.bootstrap',
  'ui.router'
]

app.config ['$stateProvider', '$urlRouterProvider', ($stateProvider, $urlRouterProvider) ->

  $urlRouterProvider.otherwise '/'

  $stateProvider
    .state 'home',
      url: '/'
      templateUrl: 'static/templates/index.html'
      controllerAs: 'home'
      controller: 'HomeCtrl'

    .state 'venues',
      url: '/venues'
      templateUrl: 'static/templates/venues.html'
      resolve:
        venues: ['Datastore', (Datastore) -> Datastore.venues() ]
      controllerAs: 'venues'
      controller: 'VenuesCtrl'

    .state 'venues.details',
      url: '/:name'
      templateUrl: 'static/templates/venues.details.html'
      resolve:
        venue: ['Datastore', '$stateParams', (Datastore, $stateParams) ->
          Datastore.venues $stateParams.name
        ]
      controllerAs: 'venue'
      controller: ['venue', class DetailsCtrl
        constructor: (venue) ->
          @details = venue.data.data
      ]

    .state 'about',
      url: '/about'
      templateUrl: 'static/templates/about.html'

]

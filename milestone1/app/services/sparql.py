from SPARQLWrapper import SPARQLWrapper, RDF, JSON
import requests


class SPARQL(object):
    def __init__(self, app):
        super(SPARQL, self).__init__()
        self._app = app
        self.REPOSITORY = 'http://stardog.krw.d2s.labs.vu.nl/group6'
        self._sparql = SPARQLWrapper(self.REPOSITORY + '/query')

        self._sparql.addParameter('reasoning','true')

    def _query(self, query, format='JSON'):
        self._sparql.setQuery(query)
        self._app.logger.debug('Running SPARQL query ' + query)

        if format == 'RDF':
            self._sparql.setReturnFormat(RDF)
        else:
            self._sparql.setReturnFormat(JSON)
            self._sparql.addParameter('Accept', 'application/sparql-results+json')

        try:
            response = self._sparql.query().convert()
            self._app.logger.debug('Got response!')
            # self._app.logger.debug(response)

            if format == 'RDF':
                return response.serialize(format='turtle')
            else:
                return response
        except Exception as e:
            self._app.logger.error('Something went wrong')
            print e
            return None

    def venues(self, format='JSON'):
        query = """
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        prefix owl: <http://www.w3.org/2002/07/owl#>
        prefix xsd: <http://www.w3.org/2001/XMLSchema#>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        prefix : <http://data.krw.d2s.labs.vu.nl/group6/findaslot/vocab/>
        prefix dbo: <http://dbpedia.org/ontology/>

        select distinct ?evenue ?venue
        where { 
            ?evenue a :Venue .
            ?evenue rdfs:label ?venue .
        }
        """
        response = self._query(query, format)
        if format == 'JSON':
            bindings = response['results']['bindings']
            return map(lambda binding: {
                'name': binding['venue']['value'],
                'href': binding['evenue']['value']
            }, bindings)
        else:
            return response


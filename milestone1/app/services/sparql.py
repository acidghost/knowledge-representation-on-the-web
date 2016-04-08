from SPARQLWrapper import SPARQLWrapper, RDF, JSON
import requests


PREFIXES = """
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix xsd: <http://www.w3.org/2001/XMLSchema#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

prefix : <http://data.krw.d2s.labs.vu.nl/group6/findaslot/vocab/>
prefix data: <http://data.krw.d2s.labs.vu.nl/group6/findaslot/resource/>
prefix dbo: <http://dbpedia.org/ontology/>
"""


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

            return response
        except Exception as e:
            self._app.logger.error('Something went wrong')
            print e
            return None


    def _deserialize_response(self, response, props=None, format='JSON'):
        if format == 'JSON':
            if props:
                return map(lambda binding:
                    { prop[1]: binding[prop[0]]['value'] for prop in props }
                , response['results']['bindings'])
            else:
                return response
        elif format == 'RDF':
            return response.serialize(format='turtle')
        else:
            return response


    def venues(self, format='JSON'):
        # use double brackets to avoid conflict with {} (placeholder)
        query = """ {}
        select distinct ?evenue ?venue ?address ?city
        where {{
            ?evenue a :Venue .
            ?evenue rdfs:label ?venue .
            ?evenue dbo:location ?elocation .
            ?elocation dbo:address ?address .
            ?elocation dbo:city ?city .
        }}
        """.format(PREFIXES)

        response = self._query(query, format=format)
        props = [('venue', 'name'), ('evenue', 'href'), ('address', 'address'), ('city', 'city')]
        return self._deserialize_response(response, props=props, format=format)


    def venue(self, name, format='JSON'):
        # use double brackets to avoid conflict with {} (placeholder)
        query = """ {0}
        prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
        prefix math: <http://www.w3.org/2005/xpath-functions/math#>

        select distinct ?venue ?eslot ?saddr ?scity ?slat ?slong ?squan ?eaddr ?ecity ?elat ?elong ?dist
        where {{
          ?eslot a :ParkingSlot ;
            rdfs:label ?slot ;
            dbo:location ?slocation ;
            :quantity ?squan .
          ?slocation geo:lat ?slat ;
            geo:long ?slong ;
            dbo:city ?scity ;
            dbo:address ?saddr .

          ?evenue a :Venue ;
            rdfs:label "{1}"^^xsd:string ;
            dbo:location ?elocation .
          bind("{1}"^^xsd:string as ?venue) .
          ?elocation geo:lat ?elat ;
            geo:long ?elong ;
            dbo:city ?ecity ;
            dbo:address ?eaddr ;

          bind(xsd:double(?slat) * math:pi() / xsd:double(180) as ?la1) .
          bind(xsd:double(?slong) * math:pi() / xsd:double(180) as ?lo1) .
          bind(xsd:double(?elat) * math:pi() / xsd:double(180) as ?la2) .
          bind(xsd:double(?elong) * math:pi() / xsd:double(180) as ?lo2) .
          bind(?lo2 - ?lo1 as ?l) .
          bind(math:acos(math:sin(?la2)*math:sin(?la1) + math:cos(?la1)*math:cos(?la1)*math:cos(?l)) * xsd:double(6371000) as ?dist) .
        }}
        order by ?dist
        limit 20
        """.format(PREFIXES, name)

        response = self._query(query, format=format)
        props = [('venue', 'venue'), ('slat', 'slot_latitude'), ('scity', 'slot_city'),
            ('slong', 'slot_longitude'), ('saddr', 'slot_address'), ('eaddr', 'venue_address'),
            ('elat', 'venue_latitude'), ('elong', 'venue_longitude'),
            ('ecity', 'venue_city'), ('squan', 'slot_quantity'), ('dist', 'distance')]
        return self._deserialize_response(response, props=props, format=format)

#!/usr/bin/env python

from SPARQLWrapper import SPARQLWrapper, JSON
import time
import argparse


LARGE_REPOSITORY = 'http://stardog.krw.d2s.labs.vu.nl/dataset'
LARGE_ENDPOINT = LARGE_REPOSITORY + '/query'
G6_REPOSITORY = 'http://stardog.krw.d2s.labs.vu.nl/group6'
G6_ENDPOINT = G6_REPOSITORY + '/query'


def run_query(query, large=True, reasoning='true'):
    """Run a SPARQL query against the endpoint"""
    sparql = SPARQLWrapper(LARGE_ENDPOINT if large else G6_ENDPOINT)

    sparql.setQuery(query)

    sparql.setReturnFormat(JSON)
    sparql.addParameter('Accept','application/sparql-results+json')

    sparql.addParameter('reasoning',reasoning)

    response = sparql.query().convert()

    return response['results']['bindings']


def timed_query(query, large=True, reasoning='false'):
    """Run a timed SPARQL query"""
    t1 = time.time()
    run_query(query, large=large, reasoning=reasoning)
    t2 = time.time()
    return t2 - t1


OUT_QUERY = '''
prefix owl: <http://www.w3.org/2002/07/owl#>
select
	distinct ?entity
	(count(distinct ?pout) as ?outdegree)
where {
	?entity a owl:Thing .
  	?entity ?pout ?somethingelse .
}
group by ?entity
order by desc(?outdegree)
'''

IN_QUERY = '''
prefix owl: <http://www.w3.org/2002/07/owl#>
select
	distinct ?entity
	(count(distinct ?pin) as ?indegree)
where {
	?entity a owl:Thing .
  	?something ?pin ?entity .
}
group by ?entity
order by desc(?indegree)
'''

Q3 = '''
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select distinct ?entity ?elabel ?type ?tlabel
where {
	?entity a <http://vivoweb.org/ontology/core#GeographicLocation> .
    ?entity rdfs:label "Amsterdam"  .
	OPTIONAL { ?type rdfs:label ?tlabel } .
}
'''

Q4 = '''
prefix : <http://data.krw.d2s.labs.vu.nl/group6/findaslot/vocab/>
prefix res: <http://data.krw.d2s.labs.vu.nl/group6/findaslot/resource/>
prefix geof: <http://www.opengis.net/def/function/geosparql/>
prefix ogc: <http://www.opengis.net/ont/geosparql#>
prefix wgs: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix dbo: <http://dbpedia.org/ontology/>
prefix unit: <http://qudt.org/vocab/unit#>

select ?spot ?saddr ?dist
where {
  bind(res:Nederlands_Marionettentheater as ?venue) .
  ?venue dbo:location ?vloc .

  ?spot a :ParkingSlot ;
  		dbo:location ?sloc .
  ?sloc dbo:address ?saddr.

  bind(geof:distance(?vloc, ?sloc, unit:Meter) as ?dist) .
}
order by asc(?dist)
'''

Q5 = '''
prefix : <http://data.krw.d2s.labs.vu.nl/group6/findaslot/vocab/>
prefix res: <http://data.krw.d2s.labs.vu.nl/group6/findaslot/resource/>
prefix geof: <http://www.opengis.net/def/function/geosparql/>
prefix ogc: <http://www.opengis.net/ont/geosparql#>
prefix wgs: <http://www.w3.org/2003/01/geo/wgs84_pos#>
prefix dbo: <http://dbpedia.org/ontology/>
prefix unit: <http://qudt.org/vocab/unit#>

select ?venue ?saddr ?dist
where {
  ?venue a :Venue ;
        dbo:location ?vloc .

  {
    select ?saddr ?dist
    where {
      ?spot a :ParkingSlot ;
			dbo:location ?sloc .
      ?sloc dbo:address ?saddr.
      bind(geof:distance(?vloc, ?sloc, unit:Meter) as ?dist) .
    }
    order by asc(?dist)
    limit 1
  }
}
'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Test SPARQL queries against a huge dataset')
    parser.add_argument(
        '-l', '--limit', type=int, help='Set a limit for the results')

    args = parser.parse_args()

    q1 = IN_QUERY + 'limit ' + str(args.limit) if args.limit else IN_QUERY
    print 'Executing Q1:', q1, '\n'
    in_time = timed_query(q1)
    print 'In-degree query executed in %i seconds\n' % in_time

    q2 = OUT_QUERY + 'limit ' + str(args.limit) if args.limit else OUT_QUERY
    print 'Executing Q2:', q2, '\n'
    out_time = timed_query(q2)
    print 'Out-degree query executed in %i seconds\n' % out_time

    q3 = Q3 + 'limit ' + str(args.limit) if args.limit else Q3
    print 'Executing Q3:', q3, '\n'
    q3_time = timed_query(q3)
    print 'Q3 query executed in %i seconds' % q3_time

    q4 = Q4 + 'limit ' + str(args.limit) if args.limit else Q4
    print 'Executing Q4 on small dataset:', q4, '\n'
    q4_time = timed_query(q4, large=False, reasoning='true')
    print 'Q4 query executed in %i seconds' % q4_time

    q5 = Q5 + 'limit ' + str(args.limit) if args.limit else Q5
    print 'Executing Q5 on small dataset:', q5, '\n'
    q5_time = timed_query(q5, large=False, reasoning='true')
    print 'Q5 query executed in %i seconds' % q5_time

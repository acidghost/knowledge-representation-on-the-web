#!/usr/bin/env python

from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime
import time


def run_query(query, reasoning='true', endpoint='http://localhost:5820/out-75/query'):
    """Run a SPARQL query against the endpoint"""
    sparql = SPARQLWrapper(endpoint)

    sparql.setQuery(query)

    sparql.setReturnFormat(JSON)
    sparql.addParameter('Accept','application/sparql-results+json')

    sparql.addParameter('reasoning',reasoning)
    sparql.setCredentials('admin', 'admin')

    response = sparql.query().convert()

    return response['results']['bindings']


def timed_query(query, reasoning='true', endpoint='http://localhost:5820/out-75/query'):
    """Run a timed SPARQL query"""
    t1 = datetime.now().microsecond
    print run_query(query, reasoning=reasoning, endpoint=endpoint)
    t2 = datetime.now().microsecond
    return t2 - t1

Q = '''
select (count(distinct ?s) as ?count)
where {
	bind(<http://aims.fao.org/aos/geopolitical.owl#Netherlands_the> as ?nl) .
	{ ?s ?p ?nl }
	union
	{ ?nl ?p ?s }
}
'''
'''
	union
	{
	?s ?p ?o .
		?o ?p1 ?nl
    }
	union
	{
	?nl ?p ?o .
		?o ?p1 ?s
    }
}
'''
endpoint = 'http://localhost:5820/out-{}/query'

if __name__ == '__main__':
    print 'Executing query out-10:', Q, '\n'
    in_time = timed_query(Q, endpoint=endpoint.format(10))
    print 'Query executed in %i microseconds\n' % in_time
    time.sleep(1)

    print 'Executing query out-20:', Q, '\n'
    in_time = timed_query(Q, endpoint=endpoint.format(20))
    print 'Query executed in %i microseconds\n' % in_time
    time.sleep(1)

    print 'Executing query out-40:', Q, '\n'
    in_time = timed_query(Q, endpoint=endpoint.format(40))
    print 'Query executed in %i microseconds\n' % in_time
    time.sleep(1)

    print 'Executing query out-75:', Q, '\n'
    in_time = timed_query(Q, endpoint=endpoint.format(75))
    print 'Query executed in %i microseconds\n' % in_time

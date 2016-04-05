#|/usr/bin/env python

import json
from rdflib import Dataset, URIRef, Literal, Namespace, RDF, RDFS, OWL, XSD
from iribaker import to_iri


with open('data/Theater.json', 'rb') as f:
    theaters = json.load(f)

    resource = 'http://data.krw.d2s.labs.vu.nl/group6/resource/'
    RESOURCE = Namespace(resource)

    vocab = 'http://data.krw.d2s.labs.vu.nl/group6/vocab/'
    VOCAB = Namespace(vocab)

    graph_uri = URIRef(resource + 'milestone1')

    dataset = Dataset()
    dataset.bind('g6data', RESOURCE)
    dataset.bind('g6vocab', VOCAB)

    graph = dataset.graph(graph_uri)

    for event_data in theaters:
        event = URIRef(to_iri(resource + event_data['title']))
        title = Literal(event_data['title'], datatype=XSD['string'])

        graph.add((event, VOCAB['title'], title))

    print dataset.serialize(format='trig')


#!/usr/bin/env python

import json
from datetime import datetime
from rdflib import Dataset, URIRef, Literal, Namespace, RDF, RDFS, OWL, XSD
from iribaker import to_iri
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint


resource = 'http://data.krw.d2s.labs.vu.nl/group6/resource/'
RESOURCE = Namespace(resource)
vocab = 'http://data.krw.d2s.labs.vu.nl/group6/vocab/'
VOCAB = Namespace(vocab)
geo = 'http://www.w3.org/2003/01/geo/wgs84_pos#'
GEO = Namespace(geo)

repo_url = "http://stardog.krw.d2s.labs.vu.nl/group6"


def convert_dataset(path, dataset, graph):
    f = open(path, 'r')
    json_data = json.load(f)

    for event_data in json_data:
        event = URIRef(to_iri(resource + event_data['title'].strip()))
        title = Literal(event_data['title'].strip(), datatype=XSD['string'])
        
        dates = event_data['dates']
        if dates != []:
            single_dates = [Literal(datetime.strptime(d, '%d-%m-%Y').date())
                for d in dates['singles']] if dates.has_key('singles') else []
            start_date = Literal(datetime.strptime(dates['startdate'], '%d-%m-%Y').date()) \
                if dates.has_key('startdate') else None
            end_date = Literal(datetime.strptime(dates['enddate'], '%d-%m-%Y').date()) \
                if dates.has_key('enddate') and dates['enddate'] != '' else None

        location_dict = event_data['location']
        location_d_name = location_dict['name'].strip()
        if location_d_name != '':
            place = URIRef(to_iri(resource + location_d_name))
            place_name = Literal(location_d_name, datatype=XSD['string'])
            location = URIRef(to_iri(resource + location_dict['adress'].strip()))
            location_address = Literal(location_dict['adress'].strip())
            location_city = Literal(location_dict['city'].strip())
            location_zip = Literal(location_dict['zipcode'].strip())
            location_lat = Literal(location_dict['latitude'].strip())
            location_lon = Literal(location_dict['longitude'].strip())

        if event_data['media']:
            medias = [(Literal(m['url'].strip(), datatype=XSD['anyURI']), m['main'].strip() == 'true') for m in event_data['media']]

        urls = [Literal(url.strip(), datatype=XSD['anyURI']) for url in event_data['urls']]

        details_dict = event_data['details']
        details = []
        for lang in details_dict.iterkeys():
            detail = {}
            if details_dict[lang]['calendarsummary'].strip() != '':
                detail['calendar_summary'] = Literal(details_dict[lang]['calendarsummary'].strip(), lang=lang)
            if details_dict[lang]['longdescription'].strip() != '':
                detail['long_description'] = Literal(details_dict[lang]['longdescription'].strip(), lang=lang)
            if details_dict[lang]['shortdescription'].strip() != '':
                detail['short_description'] = Literal(details_dict[lang]['shortdescription'].strip(), lang=lang)
            details.append(detail)

        
        graph.add((event, RDFS.label, title))
        
        if dates != []:
            for single_date in single_dates:
                graph.add((event, VOCAB['single_date'],  single_date))
            if start_date:
                graph.add((event, VOCAB['start_date'], start_date))
            if end_date:
                graph.add((event, VOCAB['end_date'], end_date))
        
        if location_dict['name'] != '':
            graph.add((event, VOCAB['place'], place))
            graph.add((place, RDFS.label, place_name))
            graph.add((place, VOCAB['location'], location))
            graph.add((location, RDFS.label, location_address))
            graph.add((location, VOCAB['address'], location_address))
            graph.add((location, VOCAB['city'], location_city))
            graph.add((location, VOCAB['zipcode'], location_zip))
            graph.add((location, GEO['lat'], location_lat))
            graph.add((location, GEO['long'], location_lon))

        if medias:
            for m in medias:
                graph.add((event, VOCAB['main_media'] if m[1] else VOCAB['media'], m[0]))

        for url in urls:
            graph.add((event, VOCAB['url'], url))

        for detail in details:
            if detail.has_key('calendar_summary'):
                graph.add((event, VOCAB['calendar_summary'], detail['calendar_summary']))
            if detail.has_key('long_description'):
                graph.add((event, VOCAB['long_description'], detail['long_description']))
            if detail.has_key('short_description'):
                graph.add((event, VOCAB['short_description'], detail['short_description']))

    return dataset, graph


def convert_parking_dataset(path, dataset, graph):
    f = open(path, 'r')
    json_data = json.load(f)

    for data in json_data['gehandicaptenparkeerplaatsen']:
        slot_data = data['node']
        
        data_address = slot_data['Adres'].strip()
        slot = URIRef(to_iri(resource + data_address))
        
        slot_loc = URIRef(to_iri(resource + data_address))
        slot_loc_address = Literal(data_address)
        
        data_quantity = slot_data['Aantal'].strip()
        slot_quantity = Literal(int(data_quantity)) if data_quantity != '' else None
        
        data_info = slot_data['Locatie-info']
        slot_info = Literal(data_info) if data_info != '' else None
        slot_loc_borough = Literal(slot_data['Stadsdeel'].strip())
        
        slot_coordinates = json.loads(slot_data['locatie'].strip())
        slot_loc_lat = Literal(slot_coordinates['coordinates'][0])
        slot_loc_long = Literal(slot_coordinates['coordinates'][1])

        
        graph.add((slot, RDFS.label, slot_loc_address))
        if slot_quantity:
            graph.add((slot, VOCAB['quantity'], slot_quantity))
        if slot_info:
            graph.add((slot, VOCAB['info'], slot_info))
        graph.add((slot, VOCAB['location'], slot_loc))
        
        graph.add((slot_loc, RDFS.label, slot_loc_address))
        graph.add((slot_loc, VOCAB['address'], slot_loc_address))
        graph.add((slot_loc, VOCAB['borough'], slot_loc_borough))
        graph.add((slot_loc, GEO['lat'], slot_loc_lat))
        graph.add((slot_loc, GEO['long'], slot_loc_long))

    return dataset, graph


def drop_stardog():
    query = "DELETE { ?s ?p ?o . } WHERE { ?s ?p ?o  . }"

    endpoint = repo_url + '/query'
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)

    sparql.setReturnFormat(JSON)
    sparql.addParameter('Accept','application/sparql-results+json')

    sparql.addParameter('reasoning','false')
    sparql.query().convert()


def upload_to_stardog(data):
    transaction_begin_url = repo_url + "/transaction/begin"
    
    # Start the transaction, and get a transaction_id
    response = requests.post(transaction_begin_url, headers={'Accept': 'text/plain'})
    transaction_id = response.content
    print 'Transaction ID', transaction_id

    # POST the data to the transaction
    post_url = repo_url + "/" + transaction_id + "/add"
    response = requests.post(post_url, data=data, headers={'Accept': 'text/plain', 'Content-type': 'application/trig'})

    # Close the transaction
    transaction_close_url = repo_url + "/transaction/commit/" + transaction_id
    response = requests.post(transaction_close_url)

    return str(response.status_code)


def serialize_upload(filename, dataset, upload=True):
    with open(filename, 'w') as f:
        dataset.serialize(f, format='trig')
    upload_to_stardog(dataset.serialize(format='trig'))


graph_uri = URIRef(resource + 'milestone1')

dataset = Dataset()
dataset.bind('g6data', RESOURCE)
dataset.bind('g6vocab', VOCAB)
dataset.default_context.parse('vocab.ttl', format='turtle')

graph = dataset.graph(graph_uri)

drop_stardog()

t_dataset, t_graph = convert_dataset('data/Theater.json', dataset, graph)
serialize_upload('data/theaters.trig', t_dataset)

mg_dataset, mg_graph = convert_dataset('data/MuseaGalleries.json', dataset, graph)
serialize_upload('data/museums.trig', mg_dataset)

park_dataset, park_graph = convert_parking_dataset('data/gehandicaptenparkeerplaatsen.json', dataset, graph)
serialize_upload('data/parking_slots.trig', park_dataset)


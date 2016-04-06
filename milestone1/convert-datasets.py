#!/usr/bin/env python

import json
from datetime import datetime
from rdflib import Dataset, URIRef, Literal, Namespace, RDF, RDFS, OWL, XSD
from iribaker import to_iri
import requests


def convert_dataset(path):
    f = open(path, 'r')
    theaters = json.load(f)

    resource = 'http://data.krw.d2s.labs.vu.nl/group6/resource/'
    RESOURCE = Namespace(resource)
    vocab = 'http://data.krw.d2s.labs.vu.nl/group6/vocab/'
    VOCAB = Namespace(vocab)
    geo = 'http://www.w3.org/2003/01/geo/wgs84_pos#'
    GEO = Namespace(geo)

    graph_uri = URIRef(resource + 'milestone1')

    dataset = Dataset()
    dataset.bind('g6data', RESOURCE)
    dataset.bind('g6vocab', VOCAB)
    dataset.default_context.parse('vocab.ttl', format='turtle')

    graph = dataset.graph(graph_uri)

    for event_data in theaters:
        event = URIRef(to_iri(resource + event_data['title']))
        title = Literal(event_data['title'], datatype=XSD['string'])
        
        dates = event_data['dates']
        if dates != []:
            single_dates = [Literal(datetime.strptime(d, '%d-%m-%Y').date())
                for d in dates['singles']] if dates.has_key('singles') else []
            start_date = Literal(datetime.strptime(dates['startdate'], '%d-%m-%Y').date()) \
                if dates.has_key('startdate') else None
            end_date = Literal(datetime.strptime(dates['enddate'], '%d-%m-%Y').date()) \
                if dates.has_key('enddate') and dates['enddate'] != '' else None

        location_dict = event_data['location']
        if location_dict['name'] != '':
            location = URIRef(to_iri(resource + location_dict['name']))
            location_name = Literal(location_dict['name'], datatype=XSD['string'])
            location_address = Literal(location_dict['adress'])
            location_city = Literal(location_dict['city'])
            location_zip = Literal(location_dict['zipcode'])
            location_lat = Literal(location_dict['latitude'])
            location_lon = Literal(location_dict['longitude'])

        if event_data['media']:
            medias = [(Literal(m['url'], datatype=XSD['anyURI']), m['main'] == 'true') for m in event_data['media']]

        urls = [Literal(url, datatype=XSD['anyURI']) for url in event_data['urls']]

        details_dict = event_data['details']
        details = []
        for lang in details_dict.iterkeys():
            detail = {}
            if details_dict[lang]['calendarsummary'] != '':
                detail['calendar_summary'] = Literal(details_dict[lang]['calendarsummary'], lang=lang)
            if details_dict[lang]['longdescription'] != '':
                detail['long_description'] = Literal(details_dict[lang]['longdescription'], lang=lang)
            if details_dict[lang]['shortdescription'] != '':
                detail['short_description'] = Literal(details_dict[lang]['shortdescription'], lang=lang)
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
            graph.add((event, VOCAB['location'], location))
            dataset.add((location, RDFS.label, location_name))
            dataset.add((location, VOCAB['address'], location_address))
            dataset.add((location, VOCAB['city'], location_city))
            dataset.add((location, VOCAB['zipcode'], location_zip))
            dataset.add((location, GEO['lat'], location_lat))
            dataset.add((location, GEO['long'], location_lon))

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

    return dataset


def upload_to_stardog(data):
    TUTORIAL_REPOSITORY = "http://stardog.krw.d2s.labs.vu.nl/group6"
    transaction_begin_url = TUTORIAL_REPOSITORY + "/transaction/begin"
    
    # Start the transaction, and get a transaction_id
    response = requests.post(transaction_begin_url, headers={'Accept': 'text/plain'})
    transaction_id = response.content
    print 'Transaction ID', transaction_id

    # POST the data to the transaction
    post_url = TUTORIAL_REPOSITORY + "/" + transaction_id + "/add"
    response = requests.post(post_url, data=data, headers={'Accept': 'text/plain', 'Content-type': 'application/trig'})

    # Close the transaction
    transaction_close_url = TUTORIAL_REPOSITORY + "/transaction/commit/" + transaction_id
    response = requests.post(transaction_close_url)

    return str(response.status_code)


t_dataset = convert_dataset('data/Theater.json')
with open('data/Theater.trig', 'w') as f:
    t_dataset.serialize(f, format='trig')
upload_to_stardog(t_dataset.serialize(format='trig'))

mg_dataset = convert_dataset('data/MuseaGalleries.json')
with open('data/MuseaGalleries.trig', 'w') as f:
    mg_dataset.serialize(f, format='trig')
upload_to_stardog(mg_dataset.serialize(format='trig'))


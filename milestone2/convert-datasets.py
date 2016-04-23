#!/usr/bin/env python

import json
from datetime import datetime
from rdflib import Dataset, Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL, XSD
from iribaker import to_iri
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint


resource = 'http://data.krw.d2s.labs.vu.nl/group6/findaslot/resource/'
RESOURCE = Namespace(resource)
vocab = 'http://data.krw.d2s.labs.vu.nl/group6/findaslot/vocab/'
VOCAB = Namespace(vocab)
geo = 'http://www.w3.org/2003/01/geo/wgs84_pos#'
GEO = Namespace(geo)
dbo = 'http://dbpedia.org/ontology/'
DBO = Namespace(dbo)
dbr = 'http://dbpedia.org/resource/'
DBR = Namespace(dbr)

repo_url = "http://stardog.krw.d2s.labs.vu.nl/group6"

VOCAB_FILE = 'vocab_v2.ttl'
SOURCE_DATA_DIR = '../source_datasets/'
OUTPUT_DIR = 'data/'


def convert_dataset(path, dataset, graph_uri, museums=True):
    f = open(path, 'r')
    json_data = json.load(f)

    graph = dataset.graph(graph_uri)
    country = URIRef(to_iri(dbr + 'Kingdom of the Netherlands'))

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
            location_city_str = location_dict['city'].strip().capitalize()
            location = URIRef(to_iri(resource + location_city_str + '/' + location_dict['adress'].strip()))
            location_city = URIRef(to_iri(dbr + location_city_str))
            location_address = Literal(location_dict['adress'].strip())
            location_zip = Literal(location_dict['zipcode'].strip())
            location_lat = Literal(float(location_dict['latitude'].replace(',', '.')))
            location_lon = Literal(float(location_dict['longitude'].replace(',', '.')))

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


        graph.add((event, RDF.type, VOCAB['Event']))
        graph.add((event, RDFS.label, title))

        if dates != []:
            for single_date in single_dates:
                graph.add((event, VOCAB['single_date'],  single_date))
            if start_date:
                graph.add((event, VOCAB['start_date'], start_date))
            if end_date:
                graph.add((event, VOCAB['end_date'], end_date))

        if location_dict['name'] != '':
            if museums:
                graph.add((event, VOCAB['exhibitionVenue'], place))
            else:
                graph.add((event, VOCAB['playVenue'], place))
            dataset.add((place, RDF.type, VOCAB['Venue']))
            dataset.add((place, RDFS.label, place_name))
            dataset.add((place, VOCAB['venueLocation'], location))
            dataset.add((location, RDF.type, VOCAB['Location']))
            dataset.add((location, RDFS.label, location_address))
            dataset.add((location, DBO['address'], location_address))
            dataset.add((location, DBO['city'], location_city))
            dataset.add((location, DBO['postalCode'], location_zip))
            dataset.add((location, DBO['country'], country))
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

    return dataset, graph


def convert_parking_dataset(path, dataset, graph_uri):
    f = open(path, 'r')
    json_data = json.load(f)

    graph = dataset.graph(graph_uri)
    country = URIRef(to_iri(dbr + 'Kingdom of the Netherlands'))
    city = URIRef(to_iri(dbr + 'Amsterdam'))

    for data in json_data['gehandicaptenparkeerplaatsen']:
        slot_data = data['node']

        data_address = slot_data['Adres'].strip()
        if data_address == '':
            continue
        slot = URIRef(to_iri(resource + data_address))

        slot_loc = URIRef(to_iri(resource + 'Amsterdam/' + data_address))
        slot_loc_address = Literal(data_address)

        data_quantity = slot_data['Aantal'].strip()
        slot_quantity = Literal(int(data_quantity), datatype=XSD['unsignedInt']) if data_quantity != '' else None

        data_info = slot_data['Locatie-info']
        slot_info = Literal(data_info) if data_info != '' else None
        slot_loc_borough = URIRef(to_iri(resource + 'Amsterdam/' + slot_data['Stadsdeel'].strip()))

        slot_coordinates = json.loads(slot_data['locatie'].strip())
        slot_loc_lat = Literal(float(slot_coordinates['coordinates'][1]))
        slot_loc_long = Literal(float(slot_coordinates['coordinates'][0]))


        graph.add((slot, RDF.type, VOCAB['ParkingSlot']))
        graph.add((slot, RDFS.label, slot_loc_address))
        if slot_quantity:
            graph.add((slot, VOCAB['quantity'], slot_quantity))
        if slot_info:
            graph.add((slot, VOCAB['info'], slot_info))
        graph.add((slot, VOCAB['slotLocation'], slot_loc))

        dataset.add((slot_loc, RDF.type, VOCAB['Location']))
        dataset.add((slot_loc, RDFS.label, slot_loc_address))
        dataset.add((slot_loc, DBO['address'], slot_loc_address))
        dataset.add((slot_loc, DBO['city'], city))
        dataset.add((slot_loc, DBO['country'], country))
        dataset.add((slot_loc_borough, RDF.type, VOCAB['Borough']))
        dataset.add((slot_loc, VOCAB['borough'], slot_loc_borough))
        dataset.add((slot_loc, GEO['lat'], slot_loc_lat))
        dataset.add((slot_loc, GEO['long'], slot_loc_long))

    return dataset, graph


def drop_stardog():
    query = "DELETE { GRAPH ?g { ?s ?p ?o }. } WHERE { GRAPH ?g { ?s ?p ?o }. }"
    query2 = "DELETE { ?s ?p ?o } WHERE { ?s ?p ?o }"

    def do_query(query):
        endpoint = repo_url + '/query'
        sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(query)

        sparql.setReturnFormat(JSON)
        sparql.addParameter('Accept','application/sparql-results+json')

        sparql.addParameter('reasoning','false')
        sparql.query().convert()

    do_query(query)
    do_query(query2)


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


graph_uri_base = resource + 'findaslot/'

drop_stardog()

dataset = Dataset()
dataset.bind('fasdat', RESOURCE)
dataset.bind('fasont', VOCAB)
dataset.bind('geo', GEO)
dataset.bind('dbo', DBO)
dataset.bind('dbr', DBR)

dataset.default_context.parse(VOCAB_FILE, format='turtle')

dataset, t_graph = convert_dataset(
    SOURCE_DATA_DIR + 'Theater.json', dataset, URIRef(graph_uri_base + 'theaters'), museums=False)
serialize_upload(OUTPUT_DIR + 'theaters.trig', t_graph)
# dataset.remove_graph(t_graph)

dataset, mg_graph = convert_dataset(
    SOURCE_DATA_DIR + 'MuseaGalleries.json', dataset, URIRef(graph_uri_base + 'museums'), museums=True)
serialize_upload(OUTPUT_DIR + 'museums.trig', mg_graph)
# dataset.remove_graph(mg_graph)

dataset, park_graph = convert_parking_dataset(
    SOURCE_DATA_DIR + 'gehandicaptenparkeerplaatsen.json', dataset, URIRef(graph_uri_base + 'parking-slots'))
serialize_upload(OUTPUT_DIR + 'parking_slots.trig', park_graph)
# dataset.remove_graph(park_graph)


# Generate VoID metadata
from rdflib.void import generateVoID
from rdflib.namespace import VOID
dcterms_uri = 'http://purl.org/dc/terms/'
DCTERMS = Namespace(dcterms_uri)

# Theaters
void_dataset_t = URIRef(graph_uri_base + 'theaters/void')
void_g_t, _ = generateVoID(t_graph, dataset=void_dataset_t)
serialize_upload(OUTPUT_DIR + 'void_theaters.trig', void_g_t)

# Museums
void_dataset_m = URIRef(graph_uri_base + 'museums/void')
void_g_mg, _ = generateVoID(mg_graph, dataset=void_dataset_m)
serialize_upload(OUTPUT_DIR + 'void_museums.trig', void_g_mg)

# Parking slots
void_dataset_ps = URIRef(graph_uri_base + 'parking-slots/void')
void_g_ps, _ = generateVoID(mg_graph, dataset=void_dataset_ps)
serialize_upload(OUTPUT_DIR + 'void_parking_slots.trig', void_g_ps)

# Generate linked dataset
void_linked_ds = URIRef(graph_uri_base + 'void')
void_linked_g = Graph()
void_linked_g.add((void_linked_ds, RDF.type, VOID.Linkset))
void_linked_g.add((void_linked_ds, VOID.target, void_dataset_t))
void_linked_g.add((void_linked_ds, VOID.target, void_dataset_m))
void_linked_g.add((void_linked_ds, VOID.target, void_dataset_ps))
void_linked_g.add((void_linked_ds, DCTERMS['subject'], DBR['Museums']))
void_linked_g.add((void_linked_ds, DCTERMS['subject'], DBR['Theaters']))
void_linked_g.add((void_linked_ds, DCTERMS['subject'], DBR['Parking_space']))
serialize_upload(OUTPUT_DIR + 'void_linked.trig', void_linked_g)


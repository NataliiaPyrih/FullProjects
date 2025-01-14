import owlready2
import requests
from urllib.parse import urlparse, unquote
import re

onto = owlready2.get_ontology("Film_blank.rdf").load()

sparql_endpoint_dbpedia = "http://dbpedia.org/sparql"

def extract_location_name(uri):
    parts = uri.split('_')
    if "in" in parts:
        idx = parts.index("in") + 1
        location_name = ' '.join(part.capitalize() for part in parts[idx:] if part[0].isupper())
        return location_name
    return ""

def get_location_info(location_name):
    query = f"""
    SELECT ?description ?lat ?long WHERE {{
      <http://dbpedia.org/resource/{location_name.replace(' ', '_')}> rdfs:comment ?description .
      <http://dbpedia.org/resource/{location_name.replace(' ', '_')}> geo:lat ?lat .
      <http://dbpedia.org/resource/{location_name.replace(' ', '_')}> geo:long ?long .
      FILTER (lang(?description) = 'en')
    }}
    """
    
    response = requests.get(sparql_endpoint_dbpedia, params={"query": query, "format": "json"})
    data = response.json()
    
    if data['results']['bindings']:
        description = data['results']['bindings'][0].get('description', {}).get('value', "No description available.")
        lat = data['results']['bindings'][0].get('lat', {}).get('value', None)
        long = data['results']['bindings'][0].get('long', {}).get('value', None)
        return description, lat, long
    return "No description available.", None, None


query_dbpedia_subjects = """
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbr: <http://dbpedia.org/resource/>

SELECT DISTINCT ?subject WHERE {
  dbr:Catch_Me_If_You_Can dcterms:subject ?subject . 
}
"""

response = requests.get(sparql_endpoint_dbpedia, params={"query": query_dbpedia_subjects, "format": "json"})
data = response.json()

subjects = [binding['subject']['value'] for binding in data['results']['bindings']]

set_in_locations = [subj for subj in subjects if "Films_set_in" in subj]
shot_in_locations = [subj for subj in subjects if "Films_shot_in" in subj]

for location_uri in set_in_locations:
    location_name = extract_location_name(location_uri)
    
    if location_name:
        location_instance = onto.Location(location_name.replace(" ", "_"))
        location_instance.hasLocationName = location_name
        
        description, lat, long = get_location_info(location_name)
        
        location_instance.hasPlaceDescription = description
        if lat and long:
            location_instance.hasGeographicalCoordinates = f"Latitude: {lat}, Longitude: {long}"
        else:
            location_instance.hasGeographicalCoordinates = None
        
        location_instance.isFilmedOnLocation = False
        location_instance.isRealLocation = True 
        
        shot_in_uri = f"http://dbpedia.org/resource/Category:Films_shot_in_{location_name.replace(' ', '_')}"
        if shot_in_uri in shot_in_locations:
            location_instance.isFilmedOnLocation = True 
        

onto.save("Film_blank.rdf")
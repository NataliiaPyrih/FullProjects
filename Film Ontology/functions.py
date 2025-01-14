from datetime import datetime
import requests


def execute_sparql(query):
    endpoint_url = "https://query.wikidata.org/sparql"
    headers = {"User-Agent": "FilmOntologyPopulation/1.0 (contact@example.com)"}
    response = requests.get(endpoint_url, params={"query": query, "format": "json"}, headers=headers)
    response.raise_for_status()
    return response.json()


def parse_date_only(date_string):
    try:
        parsed_date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        return parsed_date
    except ValueError:
        return None


def get_location_info_from_wikidata(uri):
    entity_id = uri.split("/")[-1]
    sparql_query = f"""
    SELECT ?label ?description ?latitude ?longitude WHERE {{
      wd:{entity_id} rdfs:label ?label.
      wd:{entity_id} schema:description ?description.
      OPTIONAL {{ wd:{entity_id} p:P625 ?coordinate.
                 ?coordinate psv:P625 ?coordinate_node.
                 ?coordinate_node wikibase:geoLatitude ?latitude;
                                 wikibase:geoLongitude ?longitude. }}
      FILTER (lang(?label) = "en")
      FILTER (lang(?description) = "en")
    }}
    """
    response = execute_sparql(sparql_query)

    label = None
    description = None
    lat = None
    lon = None

    if response["results"]["bindings"]:
        result = response["results"]["bindings"][0]
        label = result.get("label", {}).get("value", "")
        description = result.get("description", {}).get("value", "")
        lat = result.get("latitude", {}).get("value", "")
        lon = result.get("longitude", {}).get("value", "")
    return label, description, lat, lon
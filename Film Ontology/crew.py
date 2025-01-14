from owlready2 import get_ontology
from functions import execute_sparql, parse_date_only

onto = get_ontology("Film_blank.rdf").load()
Location = onto.Location
Film = onto.Film

def get_crew_members(film_title, role_property):
    sparql_query = f"""
    SELECT ?person ?personLabel ?birthDate ?birthPlace ?birthPlaceLabel ?nationalityLabel ?genderLabel ?notableWorkLabel WHERE {{
      ?film rdfs:label "{film_title}"@en.
      ?film wdt:{role_property} ?person.
      OPTIONAL {{ ?person wdt:P569 ?birthDate. }}
      OPTIONAL {{ ?person wdt:P19 ?birthPlace. }}
      OPTIONAL {{ ?person wdt:P27 ?nationality. }}
      OPTIONAL {{ ?person wdt:P21 ?gender. }}
      OPTIONAL {{ ?person wdt:P800 ?notableWork. }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """
    response = execute_sparql(sparql_query)

    crew_members = []
    for result in response["results"]["bindings"]:
        person_uri = result["person"]["value"]
        person_label = result.get("personLabel", {}).get("value", "")
        birth_date = result.get("birthDate", {}).get("value", None)
        birth_place_uri = result.get("birthPlace", {}).get("value", None)
        birth_place_label = result.get("birthPlaceLabel", {}).get("value", "")
        nationality = result.get("nationalityLabel", {}).get("value", "")
        gender = result.get("genderLabel", {}).get("value", "")
        notable_work = result.get("notableWorkLabel", {}).get("value", "")

        crew_members.append({
            "uri": person_uri,
            "name": person_label,
            "birth_date": parse_date_only(birth_date) if birth_date else None,
            "birth_place": {
                "uri": birth_place_uri,
                "label": birth_place_label
            } if birth_place_uri else None,
            "nationality": nationality,
            "gender": gender,
            "notable_work": notable_work
        })
    return crew_members

def get_location_info_from_wikidata(location_uri):
    sparql_query = f"""
    SELECT ?label ?description ?latitude ?longitude WHERE {{
      wd:{location_uri} rdfs:label ?label.
      wd:{location_uri} schema:description ?description.
      OPTIONAL {{
        wd:{location_uri} p:P625 ?coordinate.
        ?coordinate psv:P625 ?coordinate_node.
        ?coordinate_node wikibase:geoLatitude ?latitude;
                          wikibase:geoLongitude ?longitude.
      }}
      FILTER(LANG(?label) = "en")
      FILTER(LANG(?description) = "en")
    }}
    """
    response = execute_sparql(sparql_query)

    label = None
    description = None
    latitude = None
    longitude = None

    if "results" in response and "bindings" in response["results"]:
        result = response["results"]["bindings"]
        if result:
            label = result[0].get("label", {}).get("value", None)
            description = result[0].get("description", {}).get("value", None)
            latitude = result[0].get("latitude", {}).get("value", None)
            longitude = result[0].get("longitude", {}).get("value", None)

    return label, description, latitude, longitude

def populate_crew(film_title, crew_roles):
    film_instance = Film(film_title.replace(" ", "_"))
    film_instance.hasFilmTitle = film_title

    for role, property_id in crew_roles.items():
        crew_members = get_crew_members(film_title, property_id)
        for member in crew_members:

            crew_member_instance = onto.CrewMember(member['name'].replace(" ", "_"))
            crew_member_instance.hasParticipantName = member['name']

            if member['birth_date']:
                crew_member_instance.hasBirthDate = member['birth_date']

            if member['birth_place']:
                label, description, lat, lon = get_location_info_from_wikidata(member['birth_place']['uri'].split('/')[-1])
                location_instance = Location(label.replace(" ", "_")) if label else Location(member['birth_place']['label'].replace(" ", "_"))
                location_instance.hasLocationName = label or "Unknown"
                location_instance.hasPlaceDescription = description
                location_instance.hasGeographicalCoordinates = f"Latitude: {lat}, Longitude: {lon}" if lat and lon else None
                crew_member_instance.wasBornIn = location_instance

            if member['nationality']:
                crew_member_instance.hasNationality.append(member['nationality'])

            if member['gender']:
                crew_member_instance.hasPersonGender = member['gender']

            if member['notable_work']:
                crew_member_instance.hasWorkedOnFilms.append(member['notable_work'])

            crew_member_instance.hasPosition.append(role)

            crew_member_instance.participatedInCreation.append(film_instance)

    onto.save("Film_blank.rdf")

crew_roles = {
    "Director": "P57",
    "Screenwriter": "P58",
    "Director of Photography": "P344",
    "Film Editor": "P1040",
    "Production Designer": "P2554",
    "Costume Designer": "P2515",
    "Composer": "P86",
    "Producer": "P162"
}


populate_crew("Catch Me If You Can", crew_roles)
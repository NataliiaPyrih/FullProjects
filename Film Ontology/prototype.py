from owlready2 import get_ontology

from functions import execute_sparql,  get_location_info_from_wikidata, parse_date_only
onto = get_ontology("Film_blank.rdf").load()
Location = onto.Location

film_title = "Catch Me If You Can"

film_query = f"""
SELECT DISTINCT ?character ?characterLabel WHERE {{
  ?film rdfs:label "{film_title}"@en.
  ?film wdt:P674 ?character.  # Персонажи фильма (реальные люди)
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
"""
film_data = execute_sparql(film_query)
characters = [(binding['character']['value'], binding['characterLabel']['value']) for binding in film_data['results']['bindings']]

for character_uri, character_name in characters:
    character_id = character_uri.split('/')[-1]
    character_query = f"""
    SELECT ?genderLabel ?birthDate ?birthPlaceLabel ?deathDate ?nationalityLabel WHERE {{
      wd:{character_id} wdt:P21 ?gender;
                       wdt:P569 ?birthDate;
                       wdt:P19 ?birthPlace;
                       wdt:P27 ?nationality;
                       OPTIONAL {{ wd:{character_id} wdt:P570 ?deathDate. }}  # Дата смерти
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """
    character_data = execute_sparql(character_query)

    gender = next((binding['genderLabel']['value'] for binding in character_data['results']['bindings'] if 'genderLabel' in binding), None)
    birth_date = next((binding['birthDate']['value'] for binding in character_data['results']['bindings'] if 'birthDate' in binding), None)
    birth_place = next((binding['birthPlaceLabel']['value'] for binding in character_data['results']['bindings'] if 'birthPlaceLabel' in binding), None)
    death_date = next((binding['deathDate']['value'] for binding in character_data['results']['bindings'] if 'deathDate' in binding), None)
    nationality = next((binding['nationalityLabel']['value'] for binding in character_data['results']['bindings'] if 'nationalityLabel' in binding), None)
    alive_status = True
    
    prototype_instance = onto.Prototype(character_name.replace(" ", "_"))
    prototype_instance.hasParticipantName = character_name 

    if gender:
        prototype_instance.hasPersonGender = gender

    if birth_place:
        label, description, lat, lon = get_location_info_from_wikidata(birth_place)
        location_instance = Location(label.replace(" ", "_")) if label else Location(birth_place.replace(" ", "_"))
        location_instance.hasLocationName = label or "Unknown"
        location_instance.hasPlaceDescription = description
        location_instance.hasGeographicalCoordinates = f"Latitude: {lat}, Longitude: {lon}" if lat and lon else None
        prototype_instance.wasBornIn = location_instance

    if birth_date:
        parsed_birth_date = parse_date_only(birth_date)
        prototype_instance.hasBirthDate = parsed_birth_date

    if nationality:
        prototype_instance.hasNationality.append(nationality)

    if death_date:
        parsed_death_date = parse_date_only(death_date)
        if parsed_death_date:
            alive_status = parsed_death_date.year > 2002 
            
    prototype_instance.isAlive = alive_status
    if character_name=="Frank Abagnale":
        prototype_instance.hasParticipated = True
    else:
        prototype_instance.hasParticipated = False

onto.save("Film_blank.rdf")


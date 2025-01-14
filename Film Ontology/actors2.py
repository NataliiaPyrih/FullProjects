from owlready2 import get_ontology, locstr
from functions import execute_sparql, get_location_info_from_wikidata, parse_date_only

synonyms = {
    "the unnamed daughter of Paula and Jack": "Daughter_of_Paula",
    "FBI agents Earl Amdursky": "Earl Amdursky",
    "FBI agents Tom Fox": "Tom Fox",
    "Frank Abagnale": "Frank Abagnale_Jr."
}

def get_normalized_name(name):
    return synonyms.get(name, name.replace(" ", "_"))

def get_existing_character(name):
    normalized_name = get_normalized_name(name)
    for character in Character.instances():
        if character.name == normalized_name:
            return character
    return None

onto = get_ontology("Film_blank.rdf").load()
Location = onto.Location
Actor = onto.Actor
Extra = onto.Extra
Character = onto.Character
NeutralRole = onto.NeutralRole
Film = onto.Film

film_title = "Catch Me If You Can"
film_instance = Film(get_normalized_name(film_title))
film_instance.hasFilmTitle = film_title

film_query = f"""
SELECT DISTINCT ?actor ?actorLabel WHERE {{
  ?film rdfs:label "{film_title}"@en.
  ?film wdt:P161 ?actor.
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
"""
film_data = execute_sparql(film_query)
actors = [(binding['actor']['value'], binding['actorLabel']['value']) for binding in film_data['results']['bindings']]

role_query = """
SELECT ?actorLabel ?roleLabel ?leadingActor WHERE {
  wd:Q208108 p:P161 ?statement.  
  ?statement ps:P161 ?actor.
  OPTIONAL {
    ?statement pq:P4633 ?role.
  }
  OPTIONAL {
    ?statement pq:P3831 ?leadingActor.
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
"""
role_data = execute_sparql(role_query)
actor_roles = {
    result['actorLabel']['value']: {
        'role': result.get('roleLabel', {}).get('value', 'Unknown'),
        'leading_actor': result.get('leadingActor', {}).get('value', 'No leading actor role')
    }
    for result in role_data['results']['bindings']
}

excluded_actors = ["Frank Abagnale", "Sean Connery"]

for actor_uri, actor_name in actors:
    if actor_name in excluded_actors:
        continue

    actor_id = actor_uri.split('/')[-1]
    actor_query = f"""
    SELECT ?genderLabel ?birthDate ?birthPlace ?careerStart ?styleLabel ?filmLabel WHERE {{
      wd:{actor_id} wdt:P21 ?gender;
                   rdfs:label ?name.
      OPTIONAL {{ wd:{actor_id} wdt:P569 ?birthDate. }}
      OPTIONAL {{ wd:{actor_id} wdt:P19 ?birthPlace. }}
      OPTIONAL {{ wd:{actor_id} wdt:P2031 ?careerStart. }}
      OPTIONAL {{ wd:{actor_id} wdt:P136 ?style. }}
      OPTIONAL {{ wd:{actor_id} wdt:P800 ?film. }}
      FILTER (LANG(?name) = "en")
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """
    actor_data = execute_sparql(actor_query)

    gender = next((binding['genderLabel']['value'] for binding in actor_data['results']['bindings'] if 'genderLabel' in binding), None)
    birth_date = next((binding['birthDate']['value'] for binding in actor_data['results']['bindings'] if 'birthDate' in binding), None)
    birth_place = next((binding['birthPlace']['value'] for binding in actor_data['results']['bindings'] if 'birthPlace' in binding), None)
    career_start = next((binding['careerStart']['value'] for binding in actor_data['results']['bindings'] if 'careerStart' in binding), None)
    style = [binding['styleLabel']['value'] for binding in actor_data['results']['bindings'] if 'styleLabel' in binding]
    notable_works = [binding['filmLabel']['value'] for binding in actor_data['results']['bindings'] if 'filmLabel' in binding]

    role_info = actor_roles.get(actor_name, {})
    role = role_info.get('role', 'Unknown')
    is_leading_actor = role_info.get('leading_actor', 'No leading actor role') != 'No leading actor role'

    if role != "Unknown":
        actor_instance = Actor(get_normalized_name(actor_name))
        actor_instance.hasParticipantName = actor_name
        if is_leading_actor:
            actor_instance.isLeadingActor = True
        else:
            actor_instance.isLeadingActor = False
        
        character_name = get_normalized_name(role)
        character_instance = get_existing_character(character_name)
        if not character_instance:
            character_instance = NeutralRole(character_name)
            character_instance.hasCharacterName = role
        actor_instance.playsCharacter = [character_instance]

        if career_start:
            parsed_career_start = parse_date_only(career_start)
            if parsed_career_start:
                actor_instance.hasActingExperience = parsed_career_start
        
        if style:
            for acting_style in style:
                actor_instance.hasActingStyle.append(acting_style)
            
        if notable_works:
            actor_instance.hasWorkedOnFilms = notable_works

    else:
        actor_instance = Extra(get_normalized_name(actor_name))
        actor_instance.hasParticipantName = actor_name
        actor_instance.hasSpecialSkills = False
        actor_instance.hasWordLines = False 

    if gender:
        actor_instance.hasPersonGender = gender
        
    if birth_place:
        label, description, lat, lon = get_location_info_from_wikidata(birth_place)
        location_instance = Location(label.replace(" ", "_")) if label else Location(birth_place.replace(" ", "_"))
        location_instance.hasLocationName = label or "Unknown"
        location_instance.hasPlaceDescription = description
        location_instance.hasGeographicalCoordinates = f"Latitude: {lat}, Longitude: {lon}" if lat and lon else None
        actor_instance.wasBornIn= location_instance
        
    if birth_date:
        parsed_birth_date = parse_date_only(birth_date)
        if parsed_birth_date:
            actor_instance.hasBirthDate = parsed_birth_date

    actor_instance.filmedIn.append(film_instance)

onto.save("Film_blank.rdf")
print("Ontology updated and saved as 'Film_actors_with_roles_updated.rdf'.")
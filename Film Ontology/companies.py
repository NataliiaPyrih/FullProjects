from owlready2 import get_ontology

from functions import execute_sparql, get_location_info_from_wikidata, parse_date_only

onto = get_ontology("Film_blank.rdf").load()

Organization = onto.Organization
Location = onto.Location
Film = onto.Film

film_instance = Film("Catch_Me_If_You_Can")

film_id = "Q208108"

distributor_query = f"""
SELECT DISTINCT ?company ?companyLabel ?headquarters ?inception ?founder ?founderLabel ?revenue WHERE {{
  wd:{film_id} wdt:P750 ?company .  
  OPTIONAL {{ ?company wdt:P159 ?headquarters. }}         
  OPTIONAL {{ ?company wdt:P571 ?inception. }}            
  OPTIONAL {{ ?company wdt:P112 ?founder. }}             
  OPTIONAL {{ ?company wdt:P2139 ?revenue. }}             
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
"""

distributor_data = execute_sparql(distributor_query)
distributors = distributor_data['results']['bindings']

for distributor in distributors:
    company_label = distributor.get('companyLabel', {}).get('value', "Unknown")
    headquarters = distributor.get('headquarters', {}).get('value', None)
    inception = distributor.get('inception', {}).get('value', None)
    revenue = distributor.get('revenue', {}).get('value', None)

    company_instance = onto.search_one(iri=f"*{company_label.replace(' ', '_')}")
    if not company_instance:
        company_instance = Organization(company_label.replace(" ", "_"))
        company_instance.hasParticipantName = company_label

        if inception:
            date = parse_date_only(inception)
            company_instance.hasEstablishedDate = date if date else inception

        if headquarters:
            label, description, lat, lon = get_location_info_from_wikidata(headquarters)
            location_instance = Location(label.replace(" ", "_")) if label else Location(headquarters.replace(" ", "_"))
            location_instance.hasLocationName = label or headquarters
            location_instance.hasPlaceDescription = description
            location_instance.hasGeographicalCoordinates = f"Latitude: {lat}, Longitude: {lon}" if lat and lon else None
            company_instance.hasHeadquarters.append(location_instance)

        founders = distributor.get('founderLabel', None)
        if founders:
            if not isinstance(founders, list):
                founders = [founders]
            for founder in founders:
                founder_name = founder.get('value', 'Unknown')
                if founder_name:
                    company_instance.hasOwner.append(founder_name)

        if revenue:
            company_instance.hasRevenue = f"${int(float(revenue)):,}"

    company_instance.distributes.append(film_instance)


production_query = f"""
SELECT DISTINCT ?company ?companyLabel ?headquarters ?inception ?founder ?founderLabel WHERE {{
  wd:{film_id} wdt:P272 ?company .  
  OPTIONAL {{ ?company wdt:P159 ?headquarters. }}         
  OPTIONAL {{ ?company wdt:P571 ?inception. }}            
  OPTIONAL {{ ?company wdt:P112 ?founder. }}              
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
"""

production_data = execute_sparql(production_query)
production_companies = production_data['results']['bindings']

for production_company in production_companies:
    company_label = production_company.get('companyLabel', {}).get('value', "Unknown")
    headquarters = production_company.get('headquarters', {}).get('value', None)
    inception = production_company.get('inception', {}).get('value', None)

    company_instance = onto.search_one(iri=f"*{company_label.replace(' ', '_')}")
    if not company_instance:
        company_instance = Organization(company_label.replace(" ", "_"))
        company_instance.hasParticipantName = company_label

        if inception:
            date = parse_date_only(inception)
            company_instance.hasEstablishedDate = date if date else inception

        if headquarters:
            label, description, lat, lon = get_location_info_from_wikidata(headquarters)
            location_instance = Location(label.replace(" ", "_")) if label else Location(headquarters.replace(" ", "_"))
            location_instance.hasLocationName = label or headquarters
            location_instance.hasPlaceDescription = description
            location_instance.hasGeographicalCoordinates = f"Latitude: {lat}, Longitude: {lon}" if lat and lon else None
            company_instance.hasHeadquarters.append(location_instance)
            
        founders = production_company.get('founderLabel', None)
        if founders:
            if isinstance(founders, list):
                for founder in founders:
                    founder_name = founder.get('value', 'Unknown')
                    if founder_name:
                        company_instance.hasOwner.append(founder_name)
            else:
                founder_name = founders.get('value', 'Unknown')
                if founder_name:
                    company_instance.hasOwner.append(founder_name)

    company_instance.films.append(film_instance)


onto.save("Film_blank.rdf")
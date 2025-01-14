import owlready2
import requests

onto = owlready2.get_ontology("Film_rdf.rdf").load()

sparql_endpoint_wikidata = "https://query.wikidata.org/sparql"

query_wikidata = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?film ?title ?releaseDate ?genre ?duration ?country ?budget ?boxOffice
WHERE {
  ?film wdt:P31 wd:Q11424.
  ?film rdfs:label ?title.
  FILTER(LANG(?title) = "en")
  FILTER(REGEX(?title, "Catch Me If You Can", "i"))

  OPTIONAL { ?film wdt:P577 ?releaseDate. }
  OPTIONAL { ?film wdt:P136 ?genre. }
  OPTIONAL { ?film wdt:P2047 ?duration. }
  OPTIONAL { ?film wdt:P495 ?country. }
  OPTIONAL { ?film wdt:P2142 ?budget. }
  OPTIONAL { ?film wdt:P2130 ?boxOffice. }
}
LIMIT 1
"""

response_wikidata = requests.get(sparql_endpoint_wikidata, params={'query': query_wikidata, 'format': 'json'})
data_wikidata = response_wikidata.json()

if 'results' in data_wikidata and data_wikidata['results']['bindings']:
    film_data = data_wikidata['results']['bindings'][0]

    title = film_data['title']['value']
    release_date = film_data['releaseDate']['value']
    genre_url = film_data['genre']['value']
    duration = int(film_data['duration']['value'])
    country_url = film_data['country']['value']
    budget = float(film_data['budget']['value'])
    box_office = float(film_data['boxOffice']['value'])

    film_instance = onto.Film(title.replace(" ", "_"))
    
    film_instance.hasTitle = title
    film_instance.hasReleaseYear = int(release_date[:4])
    film_instance.hasGenre.append(genre_url.split("/")[-1])  
    film_instance.hasCountry.append(country_url.split("/")[-1])
    film_instance.hasDuration = duration
    film_instance.hasBudget = budget
    film_instance.hasBoxOffice = box_office

    print(f"Film {title} was successfully added")
else:
    print("Unable to find the film on Wikidata.")

onto.save(file="Film_blank.rdf", format="rdfxml")
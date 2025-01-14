import owlready2
import requests

onto = owlready2.get_ontology("Film_blank.rdf").load()

sparql_endpoint_dbpedia = "http://dbpedia.org/sparql"

def get_broader_categories(theme_uri):
    query = f"""
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    
    SELECT DISTINCT ?broader WHERE {{
      <{theme_uri}> skos:broader ?broader .
    }}
    LIMIT 5
    """
    
    response = requests.get(sparql_endpoint_dbpedia, params={"query": query, "format": "json"})
    data = response.json()

    broader_categories = [binding['broader']['value'] for binding in data['results']['bindings']]
    return broader_categories

def extract_themes_from_dbpedia(film_title):
    query = f"""
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbr: <http://dbpedia.org/resource/>
    
    SELECT DISTINCT ?subject WHERE {{
      dbr:{film_title.replace(' ', '_')} dcterms:subject ?subject .
    }}
    """

    response = requests.get(sparql_endpoint_dbpedia, params={"query": query, "format": "json"})
    data = response.json()

    subjects = [binding['subject']['value'] for binding in data['results']['bindings']]

    themes = [subj for subj in subjects if "Films_about" in subj]

    return themes

def create_theme_instances(film_title):
    themes = extract_themes_from_dbpedia(film_title)
    
    if not themes:
        print("No themes found for the film.")
        return []

    theme_instances = []
    for theme_uri in themes:
        theme_label = theme_uri.split("/")[-1].replace("_", " ").replace("Category:", "").replace("Films about ", "").capitalize()

        theme_instance = onto.Theme(theme_label.replace(" ", "_"))
        theme_instance.hasThemeName = theme_label

        broader_categories = get_broader_categories(theme_uri)

        if broader_categories:
            for broader_category in broader_categories:
                broader_category_label = broader_category.split(":")[-1].replace("_", " ")
                theme_instance.hasThemeCategory.append(broader_category_label)
        else:
            print("No broader categories found.")

        theme_instances.append(theme_instance)

    return theme_instances

def link_existing_film_with_themes(film_title):
    film_instance = onto.search(onto.Film, hasTitle=film_title).first()
    
    if not film_instance:
        print(f"Film '{film_title}' not found in the ontology.")
        return
    

    theme_instances = create_theme_instances(film_title)
    
    if not theme_instances:
        print("No themes to associate with the film.")
        return

    for theme in theme_instances:
        theme.isRaisedIn.append(film_instance)
        
    print(f"Film '{film_title}' successfully linked with themes.")

link_existing_film_with_themes("Catch Me If You Can")
onto.save("Film_blank.rdf")
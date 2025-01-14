from owlready2 import *

onto = get_ontology("Film_blank.rdf").load()

with onto:
    sync_reasoner_pellet()

if hasattr(onto, "Theme") or hasattr(onto.Film, "Theme"):
    theme_class = onto.Theme if hasattr(onto, "Theme") else onto.Film.Theme
    themes = list(set(theme_class.instances()))
    print(f"\nInstances of class Theme ({len(themes)}):")
    for theme in themes:
        print(f"- {theme}")
else:
    print("\nThe Theme class is not found in the ontology.")

if hasattr(onto, "Actor") or hasattr(onto.Film, "Actor"):
    actor_class = onto.Actor if hasattr(onto, "Actor") else onto.Film.Actor
    actors = list(actor_class.instances())
    print(f"\nThe number of instances of the Actor class: {len(actors)}")
else:
    print("\nThe Actor class is not found in the ontology.")
import sys
from imdb_dal import search_titles_by_name

if len(sys.argv) != 2:
    print("Usage: imdb_search_by_title <query>")
    exit(1)

query = sys.argv[1]
results = search_titles_by_name(query)

if len(results) == 0:
    print(f'No titles match “{query}.”')
    exit(0)

for title in results:
    tconst = title.get("tconst")
    name = title.get("primaryTitle")
    year = title.get("startYear")
    print(f"{tconst}  “{name}” ({year})")

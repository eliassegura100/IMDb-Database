import sys
from imdb_dal import insert_title

if len(sys.argv) != 3:
    print("Usage: imdb_add_title <title> <year>")
    exit(1)

title = sys.argv[1]
year = sys.argv[2]

try:
    year_int = int(year)
except ValueError:
    print(f'Sorry, something went wrong. Please ensure that “{year}” is a valid year.')
    exit(1)

try:
    new_title = insert_title(title, year_int)
    print(
        f'Title “{new_title.get("primaryTitle")}” '
        f'({new_title.get("startYear")}) added with ID {new_title.get("tconst")}.'
    )
except Exception as e:
    print(f"Unexpected error while inserting title: {e}")

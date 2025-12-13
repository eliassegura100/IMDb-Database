import csv

TITLE_BASICS_SOURCE = "title.basics.tsv"
TITLE_RATINGS_SOURCE = "title.ratings.tsv"
DESTINATION = "titles.csv"

ALLOWED_TITLE_TYPES = {"movie"}
MIN_VOTES = 5000
MIN_YEAR = 1990
MAX_YEAR = 2024


def parse_int(value):
    if value == r"\N":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def parse_float(value):
    if value == r"\N":
        return None
    try:
        return float(value)
    except ValueError:
        return None


print(f"Loading ratings from {TITLE_RATINGS_SOURCE}...")
ratings = {}
with open(TITLE_RATINGS_SOURCE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        tconst = row["tconst"]
        avg = parse_float(row["averageRating"])
        votes = parse_int(row["numVotes"])
        ratings[tconst] = (avg, votes)

print(f"Loaded ratings for {len(ratings):,} titles.")

print(f"Processing basics from {TITLE_BASICS_SOURCE} and writing to {DESTINATION}...")
out = open(DESTINATION, "w", newline="", encoding="utf-8")
writer = csv.writer(out)

# Header for Title nodes
writer.writerow(
    [
        "tconst",
        "titleType",
        "primaryTitle",
        "startYear",
        "runtimeMinutes",
        "averageRating",
        "numVotes",
        "genres",
    ]
)

kept = 0
seen = 0

with open(TITLE_BASICS_SOURCE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        seen += 1
        if seen % 500000 == 0:
            print(f"- Seen {seen:,} titles, kept {kept:,} so far...")

        tconst = row["tconst"]
        title_type = row["titleType"]
        is_adult = row["isAdult"]
        start_year = parse_int(row["startYear"])
        runtime_minutes = parse_int(row["runtimeMinutes"])
        genres = row["genres"]

        if title_type not in ALLOWED_TITLE_TYPES:
            continue
        if is_adult != "0":
            continue
        if start_year is None or start_year < MIN_YEAR or start_year > MAX_YEAR:
            continue

        avg_rating, num_votes = ratings.get(tconst, (None, None))
        if num_votes is None or num_votes < MIN_VOTES:
            continue

        writer.writerow(
            [
                tconst,
                title_type,
                row["primaryTitle"],
                start_year if start_year is not None else "",
                runtime_minutes if runtime_minutes is not None else "",
                avg_rating if avg_rating is not None else "",
                num_votes if num_votes is not None else "",
                genres if genres != r"\N" else "",
            ]
        )
        kept += 1

out.close()
print(f"Done. Seen {seen:,} titles, kept {kept:,}. Wrote {DESTINATION}.")

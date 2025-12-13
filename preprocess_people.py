import csv

TITLES_SOURCE = "titles.csv"
PRINCIPALS_SOURCE = "title.principals.tsv"
NAMES_SOURCE = "name.basics.tsv"
DESTINATION = "people.csv"


def load_allowed_tconsts(path):
    allowed = set()
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if not row:
                continue
            allowed.add(row[0])  # tconst is first column in titles.csv
    return allowed


print(f"Loading allowed tconst values from {TITLES_SOURCE}...")
allowed_tconsts = load_allowed_tconsts(TITLES_SOURCE)
print(f"- Loaded {len(allowed_tconsts):,} allowed titles.")

print(f"Finding people linked to those titles via {PRINCIPALS_SOURCE}...")
allowed_nconsts: set[str] = set()
seen_principals = 0

with open(PRINCIPALS_SOURCE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        seen_principals += 1
        if seen_principals % 500000 == 0:
            print(
                f"- Seen {seen_principals:,} principals rows, "
                f"collected {len(allowed_nconsts):,} people so far..."
            )
        tconst = row["tconst"]
        if tconst in allowed_tconsts:
            allowed_nconsts.add(row["nconst"])

print(
    f"Done scanning principals. Found {len(allowed_nconsts):,} people "
    "associated with filtered titles."
)

print(f"Processing people from {NAMES_SOURCE} and writing to {DESTINATION}...")
out = open(DESTINATION, "w", newline="", encoding="utf-8")
writer = csv.writer(out)

# Header for Neo4j Person nodes
writer.writerow(["nconst", "primaryName", "birthYear", "primaryProfession"])

seen_people = 0
kept_people = 0

with open(NAMES_SOURCE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        seen_people += 1
        if seen_people % 500000 == 0:
            print(f"- Seen {seen_people:,} people, kept {kept_people:,} so far...")

        nconst = row["nconst"]
        if nconst not in allowed_nconsts:
            continue

        birth_year = row["birthYear"]
        if birth_year == r"\N":
            birth_year = ""

        primary_profession = row["primaryProfession"]
        if primary_profession == r"\N":
            primary_profession = ""

        writer.writerow(
            [
                nconst,
                row["primaryName"],
                birth_year,
                primary_profession,
            ]
        )
        kept_people += 1

out.close()
print(f"Done. Seen {seen_people:,} people, kept {kept_people:,}. Wrote {DESTINATION}.")

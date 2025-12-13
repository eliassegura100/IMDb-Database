import csv

TITLES_SOURCE = "titles.csv"
PRINCIPALS_SOURCE = "title.principals.tsv"

ACTED_IN_DEST = "acted_in.csv"
DIRECTED_DEST = "directed.csv"
WROTE_DEST = "wrote.csv"

ACTING_CATEGORIES = {"actor", "actress", "self"}
DIRECTOR_CATEGORIES = {"director"}
WRITER_CATEGORIES = {"writer", "screenwriter"}


def load_allowed_tconsts(path):
    allowed = set()
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        tconst_idx = 0  # first column is tconst in titles.csv
        for row in reader:
            if not row:
                continue
            allowed.add(row[tconst_idx])
    return allowed


print(f"Loading allowed tconst values from {TITLES_SOURCE}...")
allowed_tconsts = load_allowed_tconsts(TITLES_SOURCE)
print(f"- Loaded {len(allowed_tconsts):,} allowed titles.")

acted_out = open(ACTED_IN_DEST, "w", newline="", encoding="utf-8")
directed_out = open(DIRECTED_DEST, "w", newline="", encoding="utf-8")
wrote_out = open(WROTE_DEST, "w", newline="", encoding="utf-8")

acted_writer = csv.writer(acted_out)
directed_writer = csv.writer(directed_out)
wrote_writer = csv.writer(wrote_out)

# Headers for relationship CSVs
# acted_in_header.csv
acted_writer.writerow(["nconst", "tconst", "category", "ordering"])
# directed_header.csv
directed_writer.writerow(["nconst", "tconst"])
# wrote_header.csv
wrote_writer.writerow(["nconst", "tconst"])

seen = 0
kept = 0

print(f"Processing principals from {PRINCIPALS_SOURCE}...")
with open(PRINCIPALS_SOURCE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        seen += 1
        if seen % 500000 == 0:
            print(f"- Seen {seen:,} principals rows, wrote {kept:,} edges...")

        tconst = row["tconst"]
        if tconst not in allowed_tconsts:
            continue

        nconst = row["nconst"]
        category = (row["category"] or "").lower()
        ordering = row["ordering"]
        ordering_val = None
        try:
            ordering_val = int(ordering)
        except (TypeError, ValueError):
            ordering_val = None

        if category in ACTING_CATEGORIES:
            acted_writer.writerow(
                [nconst, tconst, category, ordering_val if ordering_val is not None else ""]
            )
            kept += 1
        elif category in DIRECTOR_CATEGORIES:
            directed_writer.writerow([nconst, tconst])
            kept += 1
        elif category in WRITER_CATEGORIES:
            wrote_writer.writerow([nconst, tconst])
            kept += 1

acted_out.close()
directed_out.close()
wrote_out.close()

print(f"Done. Seen {seen:,} principals rows, wrote {kept:,} relationship rows total.")

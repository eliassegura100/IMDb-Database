import csv

TITLES_SOURCE = "titles.csv"
GENRES_DEST = "genres.csv"
TITLE_GENRES_DEST = "title_genres.csv"


print(f"Reading titles from {TITLES_SOURCE} to extract genres...")

genres_out = open(GENRES_DEST, "w", newline="", encoding="utf-8")
title_genres_out = open(TITLE_GENRES_DEST, "w", newline="", encoding="utf-8")

genres_writer = csv.writer(genres_out)
title_genres_writer = csv.writer(title_genres_out)

# genre_header.csv
genres_writer.writerow(["name"])

# title_genre_header.csv
title_genres_writer.writerow(["tconst", "genreName"])

seen_titles = 0
written_pairs = 0
seen_genres: set[str] = set()

with open(TITLES_SOURCE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        seen_titles += 1
        if seen_titles % 500000 == 0:
            print(
                f"- Seen {seen_titles:,} titles, "
                f"{len(seen_genres):,} unique genres, "
                f"{written_pairs:,} title-genre pairs..."
            )

        tconst = row["tconst"]
        genres_field = row.get("genres", "")
        if not genres_field:
            continue

        for genre in genres_field.split(","):
            genre = genre.strip()
            if not genre:
                continue

            if genre not in seen_genres:
                genres_writer.writerow([genre])
                seen_genres.add(genre)

            title_genres_writer.writerow([tconst, genre])
            written_pairs += 1

genres_out.close()
title_genres_out.close()

print(
    f"Done. Seen {seen_titles:,} titles, "
    f"found {len(seen_genres):,} genres, "
    f"wrote {written_pairs:,} title-genre pairs."
)

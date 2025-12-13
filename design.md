# IMDb Graph Design

## Logical Schema Overview

My IMDb graph focuses on titles, people, and genres.

- **Title** nodes represent movies from IMDb with properties:

  - `tconst` (ID), `titleType`, `primaryTitle`, `startYear`,
    `runtimeMinutes`, `averageRating`, `numVotes`, and `genres`.

- **Person** nodes represent cast and crew with properties:

  - `nconst`, `primaryName`, `birthYear`, and `primaryProfession`.

- **Genre** nodes represent reusable genre labels.

Relationships:

- `(:Person)-[:ACTED_IN]->(:Title)`
- `(:Person)-[:DIRECTED]->(:Title)`
- `(:Person)-[:WROTE]->(:Title)`
- `(:Title)-[:HAS_GENRE]->(:Genre)`

I chose this schema because it highlights collaboration patterns between people and titles and supports genre-based exploration.

## Preprocessing and Import

We used the IMDb non-commercial TSV datasets:

- `title.basics.tsv`
- `title.ratings.tsv`
- `name.basics.tsv`
- `title.principals.tsv`

Preprocessing scripts:

- `preprocess_titles.py` --> `titles.csv`
- `preprocess_people.py` --> `people.csv`
- `preprocess_genres.py` --> `genres.csv`, `title_genres.csv`
- `preprocess_roles.py` --> `acted_in.csv`, `directed.csv`, `wrote.csv`

Header files:

- `title_header.csv`
- `person_header.csv`
- `genre_header.csv`
- `title_genre_header.csv`
- `acted_in_header.csv`
- `directed_header.csv`
- `wrote_header.csv`

Import command (Windows):

```powershell
.\neo4j-admin.bat database import full neo4j `
  --overwrite-destination=true `
  --id-type=string `
  --nodes=Title=".../title_header.csv,.../titles.csv" `
  --nodes=Person=".../person_header.csv,.../people.csv" `
  --nodes=Genre=".../genre_header.csv,.../genres.csv" `
  --relationships=ACTED_IN=".../acted_in_header.csv,.../acted_in.csv" `
  --relationships=DIRECTED=".../directed_header.csv,.../directed.csv" `
  --relationships=WROTE=".../wrote_header.csv,.../wrote.csv" `
  --relationships=HAS_GENRE=".../title_genre_header.csv,.../title_genres.csv"

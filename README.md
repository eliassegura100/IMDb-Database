# IMDb Graph Database

A command-line application for exploring and managing IMDb film data, backed by a **Neo4j** graph database. The project includes preprocessing scripts that turn IMDb's raw TSV files into Neo4j-ready CSVs, a bulk import into Neo4j, indexes for faster search, a Data Access Layer (DAL), and a menu-driven CLI built on top of it.

Built as the final SDK project for **CMSI 3520 Database Systems** (Loyola Marymount University, Fall 2025).

---

## Table of Contents

- [Dataset](#dataset)
- [Application Features](#application-features)
- [Why Neo4j](#why-neo4j)
- [Graph Schema](#graph-schema)
- [Project Structure](#project-structure)
- [Setup and Usage](#setup-and-usage)
- [Indexing](#indexing)
- [Example Queries](#example-queries)
- [Assessment](#assessment)

---

## Dataset

This project uses the **IMDb Non-Commercial Datasets**:

- Dataset overview: https://developer.imdb.com/non-commercial-datasets
- Direct file downloads: https://datasets.imdbws.com/

The IMDb dataset is a large, public collection of metadata about films, television shows, and the people who make them. It covers titles, people (actors, directors, writers), genres, ratings, and detailed credit information such as billing order.

The following files are used and preprocessed into CSV form:

| IMDb file | Used for |
| --- | --- |
| `title.basics.tsv.gz` | Titles (name, year, runtime, type) and genres |
| `title.ratings.tsv.gz` | Ratings (average rating, number of votes) |
| `name.basics.tsv.gz` | People (name, birth year) |
| `title.principals.tsv.gz` | Roles and credits (actors, directors, writers, billing order) |

> The raw dataset files are **not** committed to this repository because of their size; `.gitignore` excludes them. Download them from the links above.

---

## Application Features

The CLI (`python/imdb_app.py`) calls into the DAL (`python/imdb_dal.py`), which holds all database logic. Users can:

- **Search titles by name** and get back IDs for further actions
- **Retrieve full title details** by ID
- **View a person's filmography**
- **Insert new titles**
- **Update existing titles**
- **Delete titles** along with all of their relationships (performed as a transaction)
- **Get top-rated titles** by genre and year range *(featured query)*
- **Find top co-stars** for a given person *(featured query)*

---

## Why Neo4j

IMDb data is naturally a graph:

- People and titles have **many-to-many** relationships (one actor appears in many films; one film has many actors).
- Relationships carry **meaningful properties**, such as billing order and role category.
- Common questions involve **multi-hop traversals**, like "who has this actor worked with?"

Neo4j models these relationships directly instead of through join tables, which makes queries such as filmographies and co-star lookups clearer and more expressive than their relational equivalents.

---

## Graph Schema

The full schema diagram is in [`IMDb Graph Schema.pdf`](IMDb%20Graph%20Schema.pdf).

<img width="1827" height="437" alt="IMDb graph schema" src="https://github.com/user-attachments/assets/17f40f07-fb11-4e69-9a0b-25ecb29ab939" />

### Node Labels

| Label | Represents |
| --- | --- |
| `(:Title)` | Movies and TV titles |
| `(:Person)` | Actors, directors, writers |
| `(:Genre)` | Genre categories |

### Relationship Types

| Relationship | Properties |
| --- | --- |
| `(:Person)-[:ACTED_IN]->(:Title)` | `category`, `ordering` |
| `(:Person)-[:DIRECTED]->(:Title)` | — |
| `(:Person)-[:WROTE]->(:Title)` | — |
| `(:Title)-[:HAS_GENRE]->(:Genre)` | — |

---

## Project Structure

```
IMDb-Database/
├── python/
│   ├── imdb_dal.py            # Data Access Layer: all Neo4j queries
│   └── imdb_app.py            # Menu-driven CLI application
├── preprocess_titles.py       # IMDb TSV → titles.csv
├── preprocess_people.py       # IMDb TSV → people.csv
├── preprocess_genres.py       # IMDb TSV → genres.csv, title_genres.csv
├── preprocess_roles.py        # IMDb TSV → acted_in.csv, directed.csv, wrote.csv
├── *_header.csv               # Neo4j import header files (one per CSV)
├── IMDb Graph Schema.pdf      # Schema diagram
├── about.md                   # Dataset, application, and design rationale
├── setup.md                   # Detailed setup instructions
├── queries.md                 # Example Cypher queries
└── group-retrospective.md
```

### Header Files

Each generated CSV has a matching header file that defines how Neo4j imports it:

`title_header.csv`, `person_header.csv`, `genre_header.csv`, `acted_in_header.csv`, `directed_header.csv`, `wrote_header.csv`, `title_genre_header.csv`

---

## Setup and Usage

### Prerequisites

- [Neo4j](https://neo4j.com/download/) (with `neo4j-admin` available)
- Python 3
- The Neo4j Python driver: `pip install neo4j`
- The IMDb TSV files listed in [Dataset](#dataset)

### 1. Preprocess the raw data

From the repository root, with the IMDb files in place:

```console
python preprocess_titles.py
python preprocess_people.py
python preprocess_genres.py
python preprocess_roles.py
```

### 2. Import into Neo4j

Run the bulk importer **while Neo4j is stopped**. Place the generated CSVs and header files where `neo4j-admin` can find them (typically Neo4j's `import` directory, or run the command from the folder containing them).

**Windows (PowerShell / Command Prompt):**

```console
.\neo4j-admin.bat database import full neo4j ^
  --overwrite-destination=true ^
  --id-type=string ^
  --nodes=Title="title_header.csv,titles.csv" ^
  --nodes=Person="person_header.csv,people.csv" ^
  --nodes=Genre="genre_header.csv,genres.csv" ^
  --relationships=ACTED_IN="acted_in_header.csv,acted_in.csv" ^
  --relationships=DIRECTED="directed_header.csv,directed.csv" ^
  --relationships=WROTE="wrote_header.csv,wrote.csv" ^
  --relationships=HAS_GENRE="title_genre_header.csv,title_genres.csv"
```

> In PowerShell, replace each trailing `^` with a backtick (`` ` ``), or put the whole command on one line.

**macOS / Linux:**

```console
neo4j-admin database import full neo4j \
  --overwrite-destination=true \
  --id-type=string \
  --nodes=Title="title_header.csv,titles.csv" \
  --nodes=Person="person_header.csv,people.csv" \
  --nodes=Genre="genre_header.csv,genres.csv" \
  --relationships=ACTED_IN="acted_in_header.csv,acted_in.csv" \
  --relationships=DIRECTED="directed_header.csv,directed.csv" \
  --relationships=WROTE="wrote_header.csv,wrote.csv" \
  --relationships=HAS_GENRE="title_genre_header.csv,title_genres.csv"
```

### 3. Start Neo4j

| Windows | macOS / Linux |
| --- | --- |
| `neo4j.bat console` | `neo4j console` |

### 4. Create indexes

In Neo4j Browser or `cypher-shell`, run the index commands in [Indexing](#indexing).

### 5. Set environment variables

The DAL reads its connection settings from environment variables.

**Windows (PowerShell):**

```powershell
$env:DB_URL="bolt://127.0.0.1:7687"
$env:DB_USER="neo4j"
$env:DB_PASSWORD="YOUR_NEO4J_PASSWORD"
```

**macOS / Linux:**

```bash
export DB_URL="bolt://localhost:7687"
export DB_USER="neo4j"
export DB_PASSWORD="YOUR_NEO4J_PASSWORD"
```

### 6. Run the application

```console
cd python
python imdb_app.py      # Windows
python3 imdb_app.py     # macOS / Linux
```

Follow the on-screen menu to search, view, create, update, and delete titles, or run the featured queries.

See [`setup.md`](setup.md) for additional setup details.

---

## Indexing

The application searches heavily by title name, person name, and genre, so these properties are indexed:

```cypher
CREATE INDEX title_primaryTitle_index IF NOT EXISTS
FOR (t:Title) ON (t.primaryTitle);

CREATE INDEX genre_name_index IF NOT EXISTS
FOR (g:Genre) ON (g.name);

CREATE INDEX person_name_index IF NOT EXISTS
FOR (p:Person) ON (p.primaryName);
```

`Title` is the largest node collection, so indexing `primaryTitle` has the biggest impact on the app's title search.

### Performance Comparison

**Example query:**

```cypher
MATCH (t:Title)
WHERE toLower(t.primaryTitle) CONTAINS "matrix"
RETURN t.primaryTitle;
```

| | Before index | After index |
| --- | --- | --- |
| Query plan (`EXPLAIN`) | Full label scan on `Title` | Uses index on `Title(primaryTitle)` |
| Execution time | Noticeably slower on large data | Significantly reduced, more predictable |

---

## Example Queries

These Cypher queries can be run in Neo4j Browser to explore the graph. More detail is in [`queries.md`](queries.md).

**Movie "ego graph":** a film with its cast, directors, and genres

```cypher
MATCH (t:Title {primaryTitle: 'The Other Side of the Wind'})
OPTIONAL MATCH (t)-[:HAS_GENRE]->(g:Genre)
OPTIONAL MATCH (p:Person)-[:ACTED_IN]->(t)
OPTIONAL MATCH (d:Person)-[:DIRECTED]->(t)
RETURN t, g, p, d;
```

**Co-star graph:** an actor's filmography and everyone they've acted alongside

```cypher
MATCH (p:Person {primaryName: 'Kirk Douglas'})-[:ACTED_IN]->(t:Title)
MATCH (co:Person)-[:ACTED_IN]->(t)
WHERE co <> p
RETURN p, t, co;
```

**Actors who also direct:** acted-in titles since 2000, plus any titles they directed

```cypher
MATCH (p:Person)-[:ACTED_IN]->(tActed:Title)
WHERE tActed.startYear >= 2000
OPTIONAL MATCH (p)-[:DIRECTED]->(tDirected:Title)
RETURN p, tActed, tDirected
LIMIT 200;
```

**Graph size summary:** counts of titles, people, genres, and relationships

```cypher
MATCH (t:Title)
WITH count(t) AS numTitles
MATCH (p:Person)
WITH numTitles, count(p) AS numPeople
MATCH (g:Genre)
WITH numTitles, numPeople, count(g) AS numGenres
MATCH ()-[r]->()
RETURN numTitles, numPeople, numGenres, count(r) AS numRelationships;
```

**Movie stats by genre:** title count, average rating, and average votes per genre

```cypher
MATCH (g:Genre)<-[:HAS_GENRE]-(t:Title)
RETURN g.name AS genre,
       count(t) AS numMovies,
       avg(t.averageRating) AS avgRating,
       avg(t.numVotes) AS avgVotes
ORDER BY numMovies DESC
LIMIT 20;
```

---

## Assessment

The IMDb dataset fit the graph model very well. Modeling roles as relationships with properties worked cleanly and showed the strengths of graph databases over relational approaches.

The main cost was preprocessing: IMDb's TSV files needed normalizing into Neo4j-compatible CSVs. Once imported, though, the data was easy to query and extend, and traversal queries such as co-stars and filmographies were much simpler to express than the equivalent relational joins.

---

## Additional Documentation

- [`about.md`](about.md): dataset, application, and design rationale
- [`setup.md`](setup.md): setup instructions
- [`queries.md`](queries.md): example queries with explanations
- [`group-retrospective.md`](group-retrospective.md): team retrospective

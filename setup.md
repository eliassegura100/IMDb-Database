## How To Run
1. Start Neo4j
    - On Windows:
      `neo4j.bat console`
    - On Mac:
      `neo4j console`

2. Set Environment Variables
    - On Windows:
      $env:DB_URL="bolt://127.0.0.1:7687"
      $env:DB_USER="neo4j"
      $env:DB_PASSWORD="YOUR_NEO4J_PASSWORD"
    
    - On Mac:
      export DB_URL="bolt://localhost:7687"
      export DB_USER="neo4j"
      export DB_PASSWORD="YOUR_NEO4J_PASSWORD"

3. Run preprocessing scripts
  python preprocess_titles.py
  python preprocess_people.py
  python preprocess_genres.py
  python preprocess_roles.py

4. Import into Neo4j
    
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
    

5. Change your dir into the python folder

6. Run this command in the terminal:
  - On Windows:
    python imdb_app.py

  - On Mac:
    python3 imdb_app.py


## Schema Diagram

The logical schema for the IMDb graph database is shown below:

Schema:
<img width="1827" height="437" alt="image" src="https://github.com/user-attachments/assets/17f40f07-fb11-4e69-9a0b-25ecb29ab939" />

## Core Node Labels

- (:Title) — movies and TV titles

- (:Person) — actors, directors, writers

- (:Genre) — genre categories

## Relationship Types

- (:Person)-[:ACTED_IN {category, ordering}]->(:Title)

- (:Person)-[:DIRECTED]->(:Title)

- (:Person)-[:WROTE]->(:Title)

- (:Title)-[:HAS_GENRE]->(:Genre)

## Preprocessing and Loaders
### Preprocessing Scripts

The following Python scripts preprocess IMDb TSV files into Neo4j-ready CSVs:

- `preprocess_titles.py`
- `preprocess_people.py`
- `preprocess_genres.py`
- `preprocess_roles.py`

## Header Files

Each CSV has a matching header file defining Neo4j import semantics, for example:

- `title_header.csv`
- `person_header.csv`
- `genre_header.csv`
- `acted_in_header.csv`
- `directed_header.csv`
- `wrote_header.csv`
- `title_genre_header.csv`

## Bulk Loader Command
The database is loaded using Neo4j’s bulk importer:

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

## Indexing
Indexes:

  
  CREATE INDEX title_primaryTitle_index IF NOT EXISTS
  FOR (t:Title)
  ON (t.primaryTitle);

  CREATE INDEX genre_name_index IF NOT EXISTS
  FOR (g:Genre)
  ON (g.name);

  CREATE INDEX person_name_index IF NOT EXISTS
  FOR (p:Person)
  ON (p.primaryName);
  

## Performance Comparison (Before vs After Indexing)

**Example Query**

  MATCH (t:Title)
  WHERE toLower(t.primaryTitle) CONTAINS "matrix"
  RETURN t.primaryTitle;

### Before Index

- `EXPLAIN` showed a full label scan on Title
- Query execution time noticeably slower on large datasets

### After Index
- `EXPLAIN` shows index usage on Title(primaryTitle)
- Significantly reduced execution time
- More predictable query performance

## Final Setup Notes
- Neo4j runs locally using Bolt (bolt://127.0.0.1:7687)
- Database access is configured via environment variables:
    - DB_URL
    - DB_USER
    - DB_PASSWORD

- All DAL operations are isolated in `imdb_dal.py`

- CLI application is implemented in `imdb_app.py`

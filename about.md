## Dataset Link
IMDb Non-Commercial Datasets
https://developer.imdb.com/non-commercial-datasets

Direct dataset files
https://datasets.imdbws.com/

## Dataset Description
The IMDb dataset is a large, publicly available collection of metadata describing films, television shows, and the people involved in their production. The dataset includes titles (movies, series, etc.), people (actors, directors, writers), genres, ratings, and detailed credit information such as casting list order.

For this project, the following IMDb TSV files were used and preprocessed into CSV form:

- `title.basics.tsv.gz` --> titles (name, year, runtime, type)

- `title.ratings.tsv.gz` --> ratings (average rating, number of votes)

- `name.basics.tsv.gz` --> people (names, birth year)

- `title.principals.tsv.gz` --> roles and credits (actors, directors, writers, casting list order)

## Application Description
This project implements a command-line IMDb application, backed by a Neo4j graph database. The application allows users to:

- Search titles by name

- Retrieve detailed title information by ID

- View a person’s filmography

- Insert new titles

- Update existing titles

- Delete titles and all associated relationships (transactional)

- Retrieve top-rated titles by genre and year range

- Find top co-stars for a given person

The application uses a Data Access Layer (`imdb_dal.py`) to collet all database logic, with helper scripts and a menu-driven CLI (`imdb_app.py`) that calls the DAL functions.

## Why Neo4j

The IMDb dataset naturally fits a graph database model:

- People and titles are entities with many-to-many relationships

- Relationships have meaningful properties such as casting list order and role category

- Queries often involve multi-hop traversals

Using Neo4j allows these relationships to be modeled directly instead of through join tables, resulting in clearer queries and more expressive traversal logic.

## After-the-Fact Assessment
The IMDb dataset fits the graph model very well. Modeling roles as relationships with properties was effective and highlighted the strengths of graph databases compared to relational approaches.

Some preprocessing complexity was required to normalize IMDb’s TSV files into Neo4j-compatible CSVs, but once imported, the data was easy to query and extend. Graph traversal queries (such as co-stars and filmographies) were much easier to express than equivalent relational joins.
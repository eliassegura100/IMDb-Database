import os
from neo4j import GraphDatabase

# Default Neo4j username is "neo4j" unless overridden
db_user = os.environ["DB_USER"] if os.environ.get("DB_USER") else "neo4j"

db = GraphDatabase.driver(
    os.environ["DB_URL"],
    auth=(db_user, os.environ["DB_PASSWORD"])
)

def search_titles_by_name(title_query, limit=100):
    """
    Search for Title nodes whose primaryTitle contains the given substring.

    Parameters:
      title_query (str): Substring to search for in primaryTitle.
        limit (int): Maximum number of results to return.

    Returns:
      list[dict]:
        Each dict has:
          - tconst (str)
          - primaryTitle (str)
          - startYear (int|None)
    Example:
      search_titles_by_name("Matrix", limit=10)
    """
    with db.session() as session:
        result = session.run(
            """
            MATCH (t:Title)
            WHERE toLower(t.primaryTitle) CONTAINS toLower($title_query)
            RETURN t.tconst AS tconst,
                t.primaryTitle AS primaryTitle,
                t.startYear AS startYear
            ORDER BY t.primaryTitle
            LIMIT $limit
            """,
            title_query=title_query,
            limit=limit
        )
        return [record.data() for record in result]
    
def get_title_by_id(tconst):
    """
    Retrieve a Title node by its tconst identifier.

    Parameters:
      tconst (str): The unique identifier of the Title.

    Returns:
      dict|None:
        If found, a dict of title properties. Otherwise None.

    Example:
      get_title_by_id("tt0133093")
    """
    with db.session() as session:
        result = session.run(
            """
            MATCH (t:Title {tconst: $tconst})
            RETURN t.tconst AS tconst,
                t.primaryTitle AS primaryTitle,
                t.startYear AS startYear,
                t.titleType AS titleType,
                t.runtimeMinutes AS runtimeMinutes,
                t.averageRating AS averageRating,
                t.numVotes AS numVotes
            """,
            tconst=tconst
        )
        row = result.single()
        return row.data() if row else None


def get_filmography_for_person(person_name, limit=100):
    """
    Given part of a person's name, return that person, their ACTED_IN edges,
    and the titles they acted in.

    Parameters:
      person_name (str): Substring to search for in person's primaryName.
        limit (int): Maximum number of results to return.

    Returns:
      list[dict]:
        Each dict has:
          - person (str)
          - tconst (str)
          - title (str)
          - year (int|None)
          - category (str|None)
          - ordering (int|None)
    Example:
        get_filmography_for_person("Keanu Reeves", limit=10)
    """
    with db.session() as session:
        result = session.run(
            """
            MATCH (p:Person)-[r:ACTED_IN]->(t:Title)
            WHERE toLower(p.primaryName) CONTAINS toLower($person_name)
            RETURN
              p.primaryName AS person,
              t.tconst AS tconst,
              t.primaryTitle AS title,
              t.startYear AS year,
              r.category AS category,
              r.ordering AS ordering
            ORDER BY year, title
            LIMIT $limit
            """,
            person_name=person_name,
            limit=limit
        )
        return [record.data() for record in result]

def insert_title(primary_title, start_year=None, title_type="movie", runtime_minutes=None):
    """
    Create a new Title node in the IMDb graph.

    Uses randomUUID() to generate a unique tconst that won't collide
    with real IMDb tconst values.

    Parameters:
      primary_title (str): The primary title of the movie/show.
      start_year (int|None): The year the movie/show started.
      title_type (str|None): The type of the title (e.g., "movie", "tvSeries").
      runtime_minutes (int|None): The runtime of the movie/show in minutes.

    Returns:
        dict:
            A dictionary of the created Title properties.
    Example:
      create_title("Test Film", start_year=2025, title_type="movie", runtime_minutes=95)
    """
    with db.session() as session:
        record = session.run(
            """
            CREATE (t:Title {
                tconst: randomUUID(),
                primaryTitle: $primary_title,
                startYear: $start_year,
                titleType: $title_type,
                runtimeMinutes: $runtime_minutes
            })
            RETURN 
                t.tconst AS tconst,
                t.primaryTitle AS primaryTitle,
                t.startYear AS startYear,
                t.titleType AS titleType,
                t.runtimeMinutes AS runtimeMinutes
            """,
            primary_title=primary_title,
            start_year=start_year,
            title_type=title_type,
            runtime_minutes=runtime_minutes
        ).single()
        return record.data() if record else None

def update_title(tconst, primary_title=None, start_year=None, title_type=None, runtime_minutes=None):
    """
    Update properties of an existing Title node in the IMDb graph.

    Parameters:
      tconst (str): The unique identifier of the Title to update.
      primary_title (str|None): New primary title (or None to keep existing).
      start_year (int|None): New start year (or None to keep existing).
      title_type (str|None): New title type (or None to keep existing).
      runtime_minutes (int|None): New runtime minutes (or None to keep existing).

    Returns:
        dict|None:
            A dictionary of the updated Title properties, or None if not found.
    Example:
        update_title("tt0133093", primary_title="The Matrix Reloaded", start_year=2003)
    """

    with db.session() as session:
        result = session.run(
            """
            MATCH (t:Title {tconst: $tconst})
            SET t.primaryTitle   = coalesce($primary_title, t.primaryTitle),
                t.startYear      = coalesce($start_year, t.startYear),
                t.titleType      = coalesce($title_type, t.titleType),
                t.runtimeMinutes = coalesce($runtime_minutes, t.runtimeMinutes)
            RETURN t.tconst AS tconst,
                t.primaryTitle AS primaryTitle,
                t.startYear AS startYear,
                t.titleType AS titleType,
                t.runtimeMinutes AS runtimeMinutes
            """,
            tconst=tconst,
            primary_title=primary_title,
            start_year=start_year,
            title_type=title_type,
            runtime_minutes=runtime_minutes
        )
        row = result.single()
        return row.data() if row else None


# Featured query 1
def get_top_titles_by_genre(genre_name, start_year=None, end_year=None, limit=20):
    """
    Retrieve top-rated titles in a given genre, optionally filtered by year range.

    Parameters:
      genre_name (str): The name of the genre to filter by (e.g., "
        start_year (int|None): Minimum start year (inclusive).
        end_year (int|None): Maximum start year (inclusive).
        limit (int): Maximum number of results to return.

    Returns:
      list[dict]:
        Each dict has:
          - tconst (str)
          - primaryTitle (str)
          - startYear (int|None)
          - averageRating (float|None)
          - numVotes (int|None)

    Example:
      get_top_titles_by_genre("Drama", start_year=1990, end_year=2010, limit=10)
    """
    with db.session() as session:
        result = session.run(
            """
            MATCH (g:Genre {name: $genre_name})<-[:HAS_GENRE]-(t:Title)
            WHERE ($start_year IS NULL OR t.startYear >= $start_year)
                AND ($end_year IS NULL OR t.startYear <= $end_year)
                AND t.averageRating IS NOT NULL
            RETURN
                t.tconst AS tconst,
                t.primaryTitle AS primaryTitle,
                t.startYear AS startYear,
                t.averageRating AS averageRating,
                t.numVotes AS numVotes
            ORDER BY t.averageRating DESC, t.numVotes DESC
            LIMIT $limit
            """,
            genre_name=genre_name,
            start_year=start_year,
            end_year=end_year,
            limit=limit
        )
        return [record.data() for record in result]

# Featured query 2
def get_top_costars(person_name_query, min_shared_credits=2, limit=20):
    """
    Given part of a person's name, find their top co-stars based on shared titles.

    Parameters:
      person_name_query (str): Substring to search for in person's primaryName.
        min_shared_credits (int): Minimum number of shared titles to consider.
        limit (int): Maximum number of results to return.

    Returns:
      list[dict]:
        Each dict has:
          - mainPerson (str)
          - costar (str)
          - sharedTitles (int)

    Example:
      get_top_costars("Keanu Reeves", min_shared_credits=2, limit=10)
    """
    with db.session() as session:
        result = session.run(
            """
            MATCH (p:Person)
            WHERE toLower(p.primaryName) CONTAINS toLower($q)
            WITH p
            ORDER BY p.primaryName
            LIMIT 1

            MATCH (p)-[:ACTED_IN]->(t:Title)<-[:ACTED_IN]-(coactor:Person)
            WHERE coactor <> p
            WITH p, coactor, COUNT(DISTINCT t) AS sharedTitles
            WHERE sharedTitles >= $min_shared
            RETURN
                p.primaryName AS mainPerson,
                coactor.primaryName AS costar,
                sharedTitles
            ORDER BY sharedTitles DESC, costar ASC
            LIMIT $limit
            """,
            q=person_name_query,
            min_shared=min_shared_credits,
            limit=limit
        )
        return [record.data() for record in result]
    
def delete_title_and_relationships(tconst):
    """
    Delete a Title node and all its relationships from the IMDb graph.

    Parameters:
        tconst (str): The unique identifier of the Title to delete.

    Returns:
        int: The number of Title nodes deleted (0 or 1).

    Example:
      delete_title_and_relationships("tt0133093")
    """
    def work(tx):
        exists = tx.run(
            "MATCH (t:Title {tconst: $tconst}) RETURN count(t) AS count",
            tconst=tconst
        ).single()["count"]

        if exists == 0:
            return 0
        
        tx.run(
            "MATCH (t:Title {tconst: $tconst}) DETACH DELETE t",
            tconst=tconst
        )
        return 1
        
    with db.session() as session:
        return session.execute_write(work)

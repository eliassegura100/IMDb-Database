## Query 1 – Movie “ego graph”: one film, its cast, director(s), and genres

This query finds one specific movie and pulls out a small ego graph around it:

- The movie node itself (`:Title`)
- All the people who acted in that movie (`:Person` with `[:ACTED_IN]`)
- Any people who directed that movie (`[:DIRECTED]`)
- All the movie’s genres (`:Genre` with `[:HAS_GENRE]`)

Cypher

```console
    MATCH (t:Title {primaryTitle: 'The Other Side of the Wind'})
    OPTIONAL MATCH (t)-[:HAS_GENRE]->(g:Genre)
    OPTIONAL MATCH (p:Person)-[:ACTED_IN]->(t)
    OPTIONAL MATCH (d:Person)-[:DIRECTED]->(t)
    RETURN t, g, p, d;
```

[Image]

## Query 2 – Co-star graph around a specific actor

This query focuses on one actor and shows:

- The actor node (:Person)

- The movies they have acted in (:Title)

- All of their co-stars in those same movies (other :Person nodes connected to the same titles)

- This is like asking: “Show me this actor’s filmography, and who they’ve worked with.”

Cypher

```console
    MATCH (p:Person {primaryName: 'Kirk Douglas'})-[:ACTED_IN]->(t:Title)
    MATCH (co:Person)-[:ACTED_IN]->(t)
    WHERE co <> p
    RETURN p, t, co;
    This produces a graph where:
```

[Image]

## Query 3 – Actors who also direct: base pattern + optional extension

This query first looks for people who act in movies. That’s the base pattern:

(p:Person)-[:ACTED_IN]->(tActed:Title)
- Then, it uses OPTIONAL MATCH to see if that same person also directs any titles:

(p)-[:DIRECTED]->(tDirected:Title)
- Actors who have never directed will still appear with just their acted-in movies. Actors who also direct will have extra nodes and edges for the movies they directed.

- I also filter to more “modern” movies and limit to keep the graph reasonable.

Cypher

```console
    MATCH (p:Person)-[:ACTED_IN]->(tActed:Title)
    WHERE tActed.startYear >= 2000
    OPTIONAL MATCH (p)-[:DIRECTED]->(tDirected:Title)
    RETURN p, tActed, tDirected
    LIMIT 200;
```

[Image]

## Query 4 – Overall aggregate: how big is my IMDb subgraph?

Returns a summary row that tells me:

- How many Title nodes I have

- How many Person nodes I have

- How many Genre nodes I have

- How many total relationships (edges) are in the graph

Cypher

```console
    // Count titles, people, genres, and all relationships
    MATCH (t:Title)
    WITH count(t) AS numTitles
    MATCH (p:Person)
    WITH numTitles, count(p) AS numPeople
    MATCH (g:Genre)
    WITH numTitles, numPeople, count(g) AS numGenres
    MATCH ()-[r]->()
    RETURN numTitles, numPeople, numGenres, count(r) AS numRelationships;
```
[Image]

## Query 5 – Grouped aggregate: movie stats by genre

This query groups by Genre and computes:

- The number of movies in each genre

- The average rating of movies in that genre

- The average number of votes (as a rough “popularity” measure)

- It’s answering: “Which genres are most common in my graph, and how do they rank on average?”

Cypher

```console
    MATCH (g:Genre)<-[:HAS_GENRE]-(t:Title)
    RETURN
    g.name AS genre,
    count(t) AS numMovies,
    avg(t.averageRating) AS avgRating,
    avg(t.numVotes) AS avgVotes
    ORDER BY numMovies DESC
    LIMIT 20;
```
[Image]


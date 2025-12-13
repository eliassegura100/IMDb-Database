**1. How well does your dataset fit the graph database model? Did anything come easier or more difficult compared to the other ones?**

The IMDb dataset fits the graph-database model extremely well. IMDb’s data is already centered around entities like titles, people, genres and relationships. These relationships naturally form connected subgraphs and ego-graphs, which worked well with Neo4j. Querying co-stars, directors, or genre-based clusters became very smooth because these are all graph-shaped questions.

**2. If you used Generative AI for this assignment, what agents did you use? What did they get correctly or incorrectly, and how did you respond?**

I mainly used ChatGPT for debugging assistance as errors occured during the process of importing data into neo4j's environment. It provided help towards how to locate and fix the issues, but ChatGPT didn't always immediately know which config file needed modification, so it took a little longer to get through the debugging assitance.
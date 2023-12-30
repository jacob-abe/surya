from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import networkx as nx
import community as community_louvain

app = FastAPI()


class ArticleSimilarities(BaseModel):
    articleSimilaritiesMap: dict


@app.get("/")
def index():
    print("Hello, World!")
    return {"message": "Hello, World!"}


@app.post("/detect-communities")
def detect_communities(data: ArticleSimilarities):
    articleSimilaritiesMap = data.articleSimilaritiesMap

    if not articleSimilaritiesMap:
        raise HTTPException(status_code=400, detail="No valid data provided")

    # Create a graph
    G = nx.Graph()
    for article, similar_articles in articleSimilaritiesMap.items():
        for similar in similar_articles:
            G.add_edge(article, similar)

    # Detect communities
    partition = community_louvain.best_partition(G)

    # Organize articles into communities
    communities = {}
    for article, community_id in partition.items():
        communities.setdefault(community_id, []).append(article)

    return communities


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, debug=True)

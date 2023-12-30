import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import networkx as nx
import community as community_louvain


class ORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return orjson.dumps(content, option=orjson.OPT_SERIALIZE_NUMPY)


app = FastAPI(
    default_response_class=ORJSONResponse,
    redoc_url=None,
    docs_url="/docs",
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["*"],
)


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
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)

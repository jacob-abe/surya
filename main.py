from flask import Flask, request, jsonify
import networkx as nx
import community as community_louvain

app = Flask(__name__)


@app.route('/')
def index():
    print("Hello, World!")
    return "Hello, World!"

@app.route('/detect-communities', methods=['POST'])
def detect_communities():
    data = request.get_json()

    if not data or 'articleSimilaritiesMap' not in data:
        return jsonify({"error": "No valid data provided"}), 400

    articleSimilaritiesMap = data['articleSimilaritiesMap']

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

    return jsonify(communities)


if __name__ == '__main__':
    app.run(debug=True)

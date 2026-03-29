import csv
import os
import random
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Graph storage (built on startup)
_graph = {}
_all_nodes = set()

def _add_edge(source, target, weight):
    if source not in _graph:
        _graph[source] = {}
    _graph[source][target] = max(_graph[source].get(target, 0.0), weight)

def _load_graph(csv_path):
    global _graph, _all_nodes
    _graph = {}
    _all_nodes = set()

    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            source = (row.get('source') or '').strip()
            target = (row.get('target') or '').strip()
            if not source or not target or source == target:
                continue

            try:
                value = float(row.get('value') or 0)
            except ValueError:
                continue

            _all_nodes.add(source)
            _all_nodes.add(target)
            _add_edge(source, target, value)
            _add_edge(target, source, value)  # use bidirectional walk as frontend logic expects


def _find_song(requested_song):
    if not requested_song:
        return None
    req_lower = requested_song.strip().lower()
    for node in _all_nodes:
        if node.strip().lower() == req_lower:
            return node
    return None


def _random_walk(start_node, num_steps=200):
    similarity_scores = {node: 0 for node in _all_nodes}
    current_node = start_node

    for _ in range(num_steps):
        neighbors = _graph.get(current_node) or {}
        if not neighbors:
            current_node = start_node
            continue

        total_weight = sum(neighbors.values())
        if total_weight <= 0:
            current_node = start_node
            continue

        r = random.random()
        cum = 0.0

        for neighbor, weight in neighbors.items():
            cum += float(weight) / total_weight
            if r <= cum:
                current_node = neighbor
                similarity_scores[neighbor] = similarity_scores.get(neighbor, 0) + 1
                break

    return sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)

@app.route('/')
def home():
    return "API is running 🚀. Use /recommend?song=your_song"
@app.route('/recommend')
def recommend():
    song = request.args.get('song')

    if not song:
        return jsonify({
            'recommendations': [],
            'error': 'Missing song query parameter',
        }), 400

    found_song = _find_song(song)
    if not found_song:
        suggestions = [s for s in list(_all_nodes) if 'artist' not in s.lower()][:5]
        return jsonify({
            'recommendations': suggestions,
            'error': f'Song "{song}" not found. Try clicking a song node directly on the graph.',
        }), 404

    if found_song not in _graph:
        suggestions = [s for s in list(_all_nodes) if 'artist' not in s.lower()][:5]
        return jsonify({
            'recommendations': suggestions,
            'error': f'No connections found for "{found_song}".',
        }), 404

    try:
        recommendations = _random_walk(found_song, num_steps=500)

        filtered = [node for node, _ in recommendations if node.strip().lower() != found_song.strip().lower()]
        top_10 = filtered[:10]

        frequent_hubs = {'Adelitas Way', 'Scream', 'Hate Love', 'Dirty Little Thing', "It's Not Over"}
        hub_recs = [r for r in top_10 if r in frequent_hubs]
        other_recs = [r for r in top_10 if r not in frequent_hubs]

        diverse = (other_recs[:3] + hub_recs[:2])[:5]
        if diverse:
            final_recs = diverse
        else:
            final_recs = top_10[:5]

        if not final_recs:
            return jsonify({
                'recommendations': [],
                'error': f'No recommendations found for "{found_song}"',
            }), 404

        return jsonify({'recommendations': final_recs}), 200

    except Exception as ex:
        return jsonify({
            'recommendations': [],
            'error': f'Internal error: {str(ex)}',
        }), 500


if __name__ == '__main__':
    csv_path = Path(__file__).resolve().parent / 'subgraph.csv'

    try:
        _load_graph(str(csv_path))
        print(f'Loaded graph nodes={len(_all_nodes)}, edges={sum(len(v) for v in _graph.values())}')
    except Exception as exc:
        print(f'ERROR loading graph: {exc}')

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

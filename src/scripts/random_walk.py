import numpy as np
import pandas as pd

def random_walk_similarity(graph, start_node, num_steps):
    """
    Computes the similarity between the start_node and all other nodes in the graph using the random walk algorithm.

    Args:
    graph: a dictionary where the keys are node names and the values are dictionaries representing the edges and their weights.
    start_node: a string representing the name of the start node.
    num_steps: an integer indicating the number of random walk steps to take.

    Returns:
    A list of tuples, where each tuple contains the name of a node and its similarity score to the start_node.
    The list is sorted in descending order of similarity scores.
    """

    # Initialize the current node and the similarity scores of all nodes to zero
    current_node = start_node
    similarity_scores = {node: 0.0 for node in graph}

    # Start the random walk from the start node
    for i in range(num_steps):
        # Compute the probabilities of transitioning to all neighboring nodes
        neighbors = graph[current_node]
        total_weight = sum(neighbors.values())
        probabilities = {node: weight / total_weight for node, weight in neighbors.items()}

        # Choose the next node based on the transition probabilities
        current_node = np.random.choice(list(probabilities.keys()), p=list(probabilities.values()))

        # Update the similarity scores of all nodes
        for node in graph:
            similarity_scores[node] += probabilities[node]

    # Sort the similarity scores in descending order and return the corresponding node names
    sorted_nodes = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)
    result = [(node, score) for node, score in sorted_nodes]

    return result



def build_graph():
    graph = dict()
    df = pd.read_csv('d3_visualization/songs_with_value.csv')
    for i in range(len(df)):
        source, target, value = df.loc[i]
        if source not in graph:
            graph[source] = {}
        
        graph[source][target] = value
    
    return graph


graph = build_graph()
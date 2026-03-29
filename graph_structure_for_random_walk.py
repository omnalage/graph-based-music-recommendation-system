class RecommendationGraph:
    
    # Initialize Graph with an empty list of nodes and edges
    
    def __init__(self):
        self.nodes = []
        self.edges = []
        
    # Add Node: The node will be comprised of just the song name and song id
    
    def addNode(self, song_name, song_id):
        self.nodes.append(Node(song_name, song_id))
    
    # Each Edge will be drawn from source to target based on the similarity
    # index of the two songs to each other. I'm not sure if the similarity
    # index is bidirectionally equivalent, but if it is that would reduce
    # the need for a DAG and we could just connect two nodes together instead
    # of worrying about distinguishing between source and target.
    
    # Additionally, within the visualization, should we scale the edges
    # based on the value of the similarity index? It is between 0 and 1 
    # after all so I think it makes sense.
    
    def addEdge(self, source, target, similarity):
        edge = []
        edge.append(source.song_id)
        edge.append(target.song_id)
        edge.append(similarity)
        self.edges.append(edge)
        
    # Each Node is created with a song name and song id    
        
class Node:
    
    def __init__(self, song_name, song_id):
        self.name = song_name
        self.song_id = song_id
        
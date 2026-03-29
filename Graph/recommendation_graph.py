import pandas as pd
import json
import numpy as np
import csv
import random

class RecommendationGraph:
    
    # Initialize Graph with an empty list of nodes and edges
    
    def __init__(self):
        self.nodes = {}
        self.song_nodes = {} #For metrics only
        self.edges = []
        self.in_edges = {}
        self.out_edges = {}
        self.artists = {}
        
    # Add Node: The node will be comprised of just the song name and song id
    
    def addNode(self, tid, node):
        self.nodes[tid] = node
    
    # Each Edge will be drawn from source to target based on the similarity
    # index of the two songs to each other. I'm not sure if the similarity
    # index is bidirectionally equivalent, but if it is that would reduce
    # the need for a DAG and we could just connect two nodes together instead
    # of worrying about distinguishing between source and target.
    
    #UPDATE: EDGES ARE NOT BIDIRECTIONALLY EQUIVALENT, SO WE ARE DEALING WITH A DAG
    
    # Additionally, within the visualization, should we scale the edges
    # based on the value of the similarity index? It is between 0 and 1 
    # after all so I think it makes sense.
    
    def addEdge(self, source, target, similarity):
        edge = []
        edge.append(source)
        edge.append(target)
        edge.append(similarity)
        edge = tuple(edge)
        self.edges.append(edge)
        if source not in self.out_edges:
            self.out_edges[source] = []
            self.out_edges[source].append(edge)
        else:
            self.out_edges[source].append(edge)
        if target not in self.in_edges:
            self.in_edges[target] = []
            self.in_edges[target].append(edge)
        else:
            self.in_edges[target].append(edge)
            
        if self.nodes[source].attribute == "song" and self.nodes[target].attribute == "song":
            self.song_nodes[source] = self.nodes[source]
            
    def random_walk_similarity(self, current_node, num_steps, num_recommendations):
        
        edges_traversed = []
        tids_traversed = []
        similarity_scores = {node: 0.0 for node in self.nodes}
        
        total_steps = 0
        
        while total_steps != num_steps:
            total_weight = 0.0
            if current_node not in self.out_edges:
                break
            for edge in self.out_edges[current_node]:
                if edge in edges_traversed or edge[1] in tids_traversed:
                    continue
                total_weight += edge[2]
            probabilities = {}
            for edge in self.out_edges[current_node]:
                if edge in edges_traversed or edge[1] in tids_traversed:
                    continue
                probabilities[edge] = edge[2] / total_weight
            keys_as_list = list(probabilities.keys())
            #print("keys_as_list: " + str(len(keys_as_list)))
            if len(keys_as_list) == 0:
                break
            chosen_idx = np.random.choice(len(keys_as_list), p = list(probabilities.values()))
            next_edge = keys_as_list[chosen_idx]
            edges_traversed.append(next_edge)
            if self.nodes[next_edge[1]].attribute == "song":
                total_steps += 1
            for edge in self.out_edges[current_node]:
                if edge in probabilities:
                    similarity_scores[edge[1]] += probabilities[edge]
            tids_traversed.append(current_node)
            current_node = next_edge[1]
            #print("num_steps " + str(total_steps))
        sorted_edges = sorted(similarity_scores.items(), key = lambda x: x[1], reverse = True)
        recommendations = {}
        scores = {}
        cnt = 0
        idx = 0
        while cnt < num_recommendations:
            if self.nodes[sorted_edges[idx][0]].attribute != "artist":
                cnt += 1
                recommendations[cnt] = sorted_edges[idx][0]
                scores[cnt] = sorted_edges[idx][1]
            idx += 1
        for k, v in recommendations.items():
            #print(str(k) + " " + str(v) + " " + str(scores[int(k)]))
        #print(recommendations)
        #print(edges_traversed)
        return recommendations, edges_traversed
        
    # Each Node is created with a song name and song id    
        
class Node:
    
    def __init__(self, attribute, song_id, song_name, song_artist, song_tags):
        self.attribute = attribute
        self.name = song_name
        self.song_id = song_id
        self.artist = song_artist
        self.tags = song_tags

def recommend(num_steps=1, num_recommendations=5):

    recommendation_graph = RecommendationGraph()
    song_info = pd.read_csv("../public/subgraph.csv")

numNodes = 1000
artist_num_songs_threshold = 3

for index, row in song_info.iterrows():
    #print(index)
    source_song_id = str(row['track_id'].strip())
    source_song_name = str(row['title'])
    source_song_artist = str(row['artist'])
    source_song_tags = row['tags']
    
    #print(source_song_id)
    #print(source_song_name)
    #print(source_song_artist)
    #print(source_song_tags)
    
    if source_song_id not in recommendation_graph.nodes and len(row['similars']) > 0:
        tmp_node = Node("song", source_song_id, source_song_name, source_song_artist, source_song_tags)
        recommendation_graph.addNode(source_song_id, tmp_node)
    
    if source_song_artist not in recommendation_graph.artists:
        recommendation_graph.artists[source_song_artist] = []
        recommendation_graph.artists[source_song_artist].append(source_song_id)
    else:
        recommendation_graph.artists[source_song_artist].append(source_song_id)
        if len(recommendation_graph.artists[source_song_artist]) == artist_num_songs_threshold:
            tmp_node = Node("artist", "N/A", source_song_artist, "N/A", "N/A")
            recommendation_graph.addNode(source_song_artist, tmp_node)
            for tid in recommendation_graph.artists[source_song_artist]:
                recommendation_graph.addEdge(source_song_id, source_song_artist, 1.0)
                recommendation_graph.addEdge(source_song_artist, source_song_id, 1.0)
        elif len(recommendation_graph.artists[source_song_artist]) > artist_num_songs_threshold:
            recommendation_graph.addEdge(source_song_id, source_song_artist, 1.0)
            recommendation_graph.addEdge(source_song_artist, source_song_id, 1.0)
    
    similar_songs = row['similars']
    similar_songs = similar_songs.replace('[','')
    similar_songs = similar_songs.replace("'", '')
    similar_songs = similar_songs.replace(" ", '').split('],')
    
    for song in similar_songs:
        song = song.replace(']', '')
        splitted_song = song.split(',')
        if len(splitted_song) != 2:
            continue
        target_id = str(splitted_song[0].strip())
        similarity_index = splitted_song[1]
        if target_id not in recommendation_graph.nodes:
            target_name = "Null"
            target_artist = "Null"
            target_tags = None
            if target_id in song_info['track_id'].values:
                target_name = str(song_info.loc[song_info['track_id'] == target_id]['title'].values[0])
                target_artist = str(song_info.loc[song_info['track_id'] == target_id]['artist'].values[0])
                target_tags = song_info.loc[song_info['track_id'] == target_id]['tags'].values[0]
            else:
                continue
            tmp_node = Node("song", target_id, target_name, target_artist, target_tags)
            recommendation_graph.addNode(target_id, tmp_node)
            
        #print(target_id)
        #print(target_name)
        #print(target_artist)
        #print(target_tags)
        
        recommendation_graph.addEdge(source_song_id, target_id, float(similarity_index))
        
        if target_artist not in recommendation_graph.artists and (not target_name == "Null"):
            recommendation_graph.artists[target_artist] = []
            recommendation_graph.artists[target_artist].append(target_id)
        elif target_artist in recommendation_graph.artists:
            recommendation_graph.artists[target_artist].append(target_id)
            if len(recommendation_graph.artists[target_artist]) == artist_num_songs_threshold:
                tmp_node = Node("artist", "N/A", source_song_artist, "N/A", "N/A")
                recommendation_graph.addNode(target_artist, tmp_node)
                for tid in recommendation_graph.artists[target_artist]:
                    recommendation_graph.addEdge(tid, target_artist, 1.0)
                    recommendation_graph.addEdge(target_artist, tid, 1.0)
            elif len(recommendation_graph.artists[target_artist]) > artist_num_songs_threshold:
                recommendation_graph.addEdge(target_id, target_artist, 1.0)
                recommendation_graph.addEdge(target_artist, target_id, 1.0)
    
    if len(recommendation_graph.nodes) >= numNodes:
        break
            
#print(len(recommendation_graph.nodes))
#print(len(recommendation_graph.edges))

#for tid in recommendation_graph.nodes:
    #print(tid)
    #if tid in recommendation_graph.in_edges:
        #print(len(recommendation_graph.in_edges[tid]))
    #else:
        #print(str(0))
    #if tid in recommendation_graph.out_edges:
        #print(len(recommendation_graph.out_edges[tid]))
    #else:
        #print(str(0))
    #print("-----------------------------------------")
recommendation_graph.random_walk_similarity('TRAAAAK128F9318786', 3, 5)

header = ['source', 's_attribute', 's_id', 's_artist', 'target', 't_attribute', 
          't_id', 't_artist', 'value', 's_tags', 't_tags']

f = open('subgraph.csv', 'w', encoding = 'utf-8', newline = '')
writer = csv.writer(f)
writer.writerow(header)
for edge in recommendation_graph.edges:
    source = recommendation_graph.nodes[edge[0]].name
    s_attribute = recommendation_graph.nodes[edge[0]].attribute
    s_id = recommendation_graph.nodes[edge[0]].song_id
    s_artist = recommendation_graph.nodes[edge[0]].artist
    target = recommendation_graph.nodes[edge[1]].name
    t_attribute = recommendation_graph.nodes[edge[1]].attribute
    t_id = recommendation_graph.nodes[edge[1]].song_id
    t_artist = recommendation_graph.nodes[edge[1]].artist
    value = edge[2]
    s_tags = recommendation_graph.nodes[edge[0]].tags
    t_tags = recommendation_graph.nodes[edge[1]].tags
    row = [source, s_attribute, s_id, s_artist, target, t_attribute, t_id, t_artist, value, s_tags, t_tags]
    writer.writerow(row)
    f.flush()
f.close()

#print("--------------------------------------------")

#Metrics

randomly_chosen_songs = list(np.random.choice(list(recommendation_graph.song_nodes.keys()), 5, 
                                         p =  [1 / len(list(recommendation_graph.song_nodes.keys())) 
                                               for _ in recommendation_graph.song_nodes.keys()]))

init_len = len(randomly_chosen_songs)

for i in range(init_len):
    tmp = [edge for edge in recommendation_graph.out_edges[randomly_chosen_songs[i]] if float(edge[2]) > 0.001]
    added_song = random.choice(tmp)[1]
    randomly_chosen_songs.append(added_song)
        
        
randomly_chosen_songs_set = set()
for song in randomly_chosen_songs:
    randomly_chosen_songs_set.add(song)

#print(randomly_chosen_songs)

input_songs = list(np.random.choice(list(randomly_chosen_songs), 5, p = [0.1 for _ in randomly_chosen_songs]))

#print("--------------------------------------------------------")
#print(input_songs)

sum_of_avg_ratios = 0.0
for j in range(100):
    sum_of_ratios = 0.0
    for song in input_songs:
        #print("song: " + str(song))
        #print("------------------------------------------")
        recommendations, edges = recommendation_graph.random_walk_similarity(song, 2, 5)
        tp = 0
        total = len(list(recommendations.keys()))
        for recommendation in recommendations:
            if recommendations[recommendation] in randomly_chosen_songs_set and recommendations[recommendation] not in input_songs:
                tp += 1
                randomly_chosen_songs_set.remove(recommendations[recommendation])
        ratio = float(tp) / total
        #print(ratio)
        sum_of_ratios += ratio
    average_ratio = sum_of_ratios / len(input_songs)
    sum_of_avg_ratios += average_ratio
#print(sum_of_avg_ratios / 100.0)
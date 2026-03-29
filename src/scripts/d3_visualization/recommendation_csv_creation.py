import networkx as nx
import matplotlib.pyplot as plt
import csv

# Get user input for the song
song = input('Enter a song: ')

#Use other code to get recommended songs

# Hardcoded list of recommended songs
songs = [
    ('Shape of You', 'Ed Sheeran'),
    ('Castle on the Hill', 'Ed Sheeran'),
    ('Don\'t', 'Ed Sheeran'),
    ('Rockabye', 'Clean Bandit ft. Sean Paul & Anne-Marie'),
    ('Symphony', 'Clean Bandit ft. Zara Larsson'),
    ('Don\'t Start Now', 'Dua Lipa'),
    ('Levitating', 'Dua Lipa'),
    ('Physical', 'Dua Lipa'),
    ('Blinding Lights', 'The Weeknd'),
    ('Heartless', 'The Weeknd'),
    ('Save Your Tears', 'The Weeknd & Ariana Grande'),
    ('Positions', 'Ariana Grande'),
    ('Watermelon Sugar', 'Harry Styles'),
    ('Locked Out of Heaven', 'Bruno Mars'),
    ('Treasure', 'Bruno Mars'),
    ('Uptown Funk', 'Mark Ronson ft. Bruno Mars'),
    ('Can\'t Stop the Feeling!', 'Justin Timberlake'),
    ('Get Lucky', 'Daft Punk ft. Pharrell Williams'),
    ('Love Again', 'Dua Lipa'),
    ('New Rules', 'Dua Lipa'),
    ('Say So', 'Doja Cat')
]

# Create a graph and add nodes for each song
graph = nx.Graph()
for song, artist in songs:
    graph.add_node(song)

# Add edges between songs that have the same artist and assign 0 to each edge
for i in range(len(songs)):
    for j in range(i+1, len(songs)):
        if songs[i][1] == songs[j][1]:
            graph.add_edge(songs[i][0], songs[j][0], value=0)

# Write the graph to a CSV file
with open('songs_with_value.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['source', 'target', 'value'])
    for edge in graph.edges(data=True):
        writer.writerow([edge[0], edge[1], edge[2]['value']])

# Draw the graph- this was just a test. It will be used with my code from HW2
nx.draw_networkx(graph)
plt.show()
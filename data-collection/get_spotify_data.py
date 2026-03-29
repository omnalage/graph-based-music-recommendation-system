import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from tqdm import tqdm
import csv
from dotenv import load_dotenv
import os
import sys
import time

# TODO: use spotify "get_several_tracks" to scrape song popular/song_genre and artist followers/genre association
# CURRENTLY ONLY USING SPOTIFY API TO GET MORE METADATA FOR A GIVEN SONG
# TODO: USE SPOTIFY API TO GET MORE SONGS (that are not in MSD subset/MSD full)
def save_song_id_and_artist_id(sp, filepath, ids_save_path, start_from=0):
    # get data
    data = None
    # with open("../data/info_for_spotify_api.csv", "r") as f:
    #     data = f.read().splitlines()[1 + start_from:] # skip line 1 (header)
    # with open("../data/lastfm_train_test_comb-1.csv", "r") as f:
    with open(filepath, "r") as f:
        data = f.read().splitlines()[1 + start_from:] # skip line 1 (header)

    # make sure data exists
    if data == None:
        return
    
    # vars to keep track of how many songs we found and didn't find
    didnt_find = 0
    found = 0
    
    # mode settings in case error occurred and we need to restart from a specific index
    mode = "w"
    if start_from != 0:
        mode = "a"

    with open(ids_save_path, mode) as f:
        writer = csv.writer(f)

        if mode == "w":
            writer.writerow(["song_name", "song_id", "artist_name", "artist_id"])
        
        for dat in tqdm(data):
            written_to_csv = False
            # song_name, artist = tuple(dat.split(","))
            song_name, artist = tuple(dat.split(",")[1:3])
            sn, sid, an, aid = song_name, None, artist, None

            # iterate through all pages of search results
            more_entries_to_search = True
            offset = 0
            while more_entries_to_search or not written_to_csv:
                q = f"track:{song_name} artist:{artist}"

                try:
                    search_results = sp.search(q=q, limit=50, offset=offset, type='track')
                    time.sleep(0.5) # time buffer to avoid rate limit
                except spotipy.SpotifyException as e:
                    print("ERROR: ", e)
                    print("EXCEPTION OCCURRED: writing %s, %s, %s, %s" % (sn, sid, an, aid))
                    didnt_find += 1
                    writer.writerow([sn, sid, an, aid])
                    written_to_csv = True
                    break

                # find search result that matches song_name and artist
                for result in search_results["tracks"]["items"]:
                    if result == None:
                        more_entries_to_search = False
                        break

                    if result["name"] == song_name and result["artists"][0]["name"] == artist:
                        sn, sid, an, aid = song_name, result["id"], artist, result["artists"][0]["id"]
                        # print("FOUND MATCHING RESULT: writing %s, %s, %s, %s" % (sn, sid, an, aid))
                        found += 1
                        writer.writerow([sn, sid, an, aid])

                        written_to_csv = True
                        more_entries_to_search = False
                        break

                # stop if no more search results
                if search_results["tracks"]["next"] == None or len(search_results["tracks"]["items"]) == 0:
                    more_entries_to_search = False

                if more_entries_to_search == False and written_to_csv == False:
                    # print("DIDN'T FIND MATCH & DIDN'T WRITE writing %s, %s, %s, %s" % (sn, sid, an, aid))
                    didnt_find += 1
                    writer.writerow([sn, sid, an, aid])
                    written_to_csv = True
                offset += 50

    # print("didn't find: %d\nfound: %d" % (didnt_find, found))
    print(didnt_find, found)

def save_song_features(sp, ids_path, collected_data_save_path):
    # get data from file
    data = None
    with open(ids_path, "r") as f:
        data = f.read().splitlines()[1:] # skip line 1 (header)
    
    # check if data exists
    if data == None:
        print(f"data from {ids_path} is None")
        return
    
    # collect data with Spotify API
    with open(collected_data_save_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["song_name", "artist_name", "danceability", "energy", "key", "loudness", "mode", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "duration_ms", "time_signature"])

        # keys that we want to collect
        valid_keys = ["danceability", "energy", "key", "loudness", "mode", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "duration_ms", "time_signature"]

        # x_count = 0
        count = 0
        song_names = []
        artist_names = []
        song_ids = []
        for dat in tqdm(data):
            song_name, song_id, artist, artist_id = tuple(dat.split(","))

            if not song_id:
                song_id= "x" # "x" is a placeholder that we can send to Spotify API to return None (helps with indexing)
                # x_count += 1
            
            # add to temp group of 100 song ids
            song_names.append(song_name)
            artist_names.append(artist)
            song_ids.append(song_id)
            
            # save group of 100 song ids, reset to continue collecting
            if count == 99:
                count = 0

                search_results = sp.audio_features(tracks=song_ids)

                for i, res_dict in enumerate(search_results):
                    if res_dict == None:
                        writer.writerow([song_names[i], artist_names[i], None, None, None, None, None, None, None, None, None, None, None, None, None])
                        continue

                    row_to_write = [song_names[i], artist_names[i]]
                    for k, v, in res_dict.items():
                        if k in valid_keys:
                            row_to_write.append(v)

                    writer.writerow(row_to_write)

                song_names = []
                artist_names = []
                song_ids = []
                time.sleep(0.33) # time buffer to avoid rate limit
            else:
                count += 1
    # print("number of missing ids %d" % x_count)

def save_song_analysis(client_id, client_secret, ids_path, collected_data_save_path):
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # get data from file
    data = None
    with open(ids_path, "r") as f:
        data = f.read().splitlines()[1:] # skip line 1 (header)
    
    # check if data exists
    if data == None:
        return
    
    # collect data with Spotify API
    with open(collected_data_save_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["song_name", "artist_name", "danceability", "energy", "key", "loudness", "mode", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "duration_ms", "time_signature"])

        # keys that we want to collect
        # valid_keys = ["danceability", "energy", "key", "loudness", "mode", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "duration_ms", "time_signature"]

        count = 0
        for dat in tqdm(data):
            song_name, song_id, artist, artist_id = tuple(dat.split(","))
            count += 1

            if not song_id: # aka song_id doesn't exist
                # writer.writerow(null stuffs)
                continue
            
            search_results = sp.audio_analysis(song_id)
            time.sleep(0.33) # time buffer to avoid rate limit

            # for i, res_dict in enumerate(search_results):
            #     f.write(str(res_dict))
            #     f.write("\n\n")
            f.write(str(search_results))
            f.write("\n\n")

def count_lines_in_file(filepath):
    line_count = 0
    with open(filepath, "r") as f:
        csv_reader = csv.reader(f)

        for line in csv_reader:
            line_count += 1

    print(f"Number of lines in {filepath}: {line_count}")

def spotify_api_authentication():
    load_dotenv()
    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")
    
    # for debugging
    # print(client_id)
    # print(client_secret)

    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

if __name__ == "__main__":
    sp = spotify_api_authentication()
    
    datapath = "../data/"

#     # NOTE: ONLY CALL ONCE TO GET IDs
#     # print("collecting song and artist ids...")
#     # save_song_id_and_artist_id(client_id, client_secret, datapath + "spotify_api_ids.csv", 0) 
#     # count_lines_in_file(datapath + "spotify_api_ids2.csv")
    split_num = 5
    # save_song_id_and_artist_id(sp, datapath + f"lastfm_train_test_comb-{split_num}.csv", datapath + f"lastfm_train_test_comb-{split_num}_spotify_ids.csv", 0)

    # print("saving song feature info...")
    # filename = "spotify_api_song_features_data_unclean.csv"
    # save_song_features(sp, datapath + "spotify_api_ids.csv", datapath + filename)
    # count_lines_in_file(datapath + filename)
    filename = f"lastfm_train_test_comb-{split_num}_spotify_features_data_unclean.csv"
    save_song_features(sp, datapath + f"lastfm_train_test_comb-{split_num}_spotify_ids.csv", datapath + filename)

    # TODO: NOT USING FOR NOW... too much detailed data I don't understand
    # print("saving song analysis info...")
    # filename = "spotify_api_song_analysis_data_unclean.csv"    
    # save_song_analysis(client_id, client_secret, datapath + "spotify_api_ids.csv", datapath + filename)
    # count_lines_in_file(datapath + filename)
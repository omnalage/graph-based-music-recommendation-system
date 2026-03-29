# we should try to work with tar (so we don't actually need to extract 300 GB of data when it comes to the full dataset)
# import tarfile

# with tarfile.open("../data/millionsongsubset.tar.gz", "r:gz") as tar:
    # tar.extractall(path="../data/tmp") # extract tar file

    # top_level_dir = os.path.commonprefix(tar.getnames())

    # files = [os.path.join("../data/tmp/top_level_dir", filename) for filename in tar.getnames() if tar.endswith(".h5")]
    # print(files[:3])

import numpy as np
import h5py
import pandas as pd
import os
import csv
from tqdm import tqdm

'''
/analysis/songs
Index(['analysis_sample_rate', 'audio_md5', 'danceability', 'duration',
    'end_of_fade_in', 'energy', 'idx_bars_confidence', 'idx_bars_start',
    'idx_beats_confidence', 'idx_beats_start', 'idx_sections_confidence',
    'idx_sections_start', 'idx_segments_confidence',
    'idx_segments_loudness_max', 'idx_segments_loudness_max_time',
    'idx_segments_loudness_start', 'idx_segments_pitches',
    'idx_segments_start', 'idx_segments_timbre', 'idx_tatums_confidence',
    'idx_tatums_start', 'key', 'key_confidence', 'loudness', 'mode',
    'mode_confidence', 'start_of_fade_out', 'tempo', 'time_signature',
    'time_signature_confidence', 'track_id'],
    dtype='object')

/metadata/songs
Index(['analyzer_version', 'artist_7digitalid', 'artist_familiarity',
    'artist_hotttnesss', 'artist_id', 'artist_latitude', 'artist_location',
    'artist_longitude', 'artist_mbid', 'artist_name', 'artist_playmeid',
    'genre', 'idx_artist_terms', 'idx_similar_artists', 'release',
    'release_7digitalid', 'song_hotttnesss', 'song_id', 'title',
    'track_7digitalid'],
    dtype='object')

/musicbrainz/songs
Index(['idx_artist_mbtags', 'year'], dtype='object')
'''

def walkdir(folder):
    """Walk through each files in a directory"""
    for root, _, files in os.walk(folder):
        for filename in files:
            yield os.path.abspath(os.path.join(root, filename))

def get_all_data():
    with open("../data/msd_subset_data_songs_unclean.csv", "w") as f:
        writer = csv.writer(f) # create the csv writer

        writer.writerow(['analysis_sample_rate', 'audio_md5', 'danceability', 'duration',
        'end_of_fade_in', 'energy', 'idx_bars_confidence', 'idx_bars_start',
        'idx_beats_confidence', 'idx_beats_start', 'idx_sections_confidence',
        'idx_sections_start', 'idx_segments_confidence',
        'idx_segments_loudness_max', 'idx_segments_loudness_max_time',
        'idx_segments_loudness_start', 'idx_segments_pitches',
        'idx_segments_start', 'idx_segments_timbre', 'idx_tatums_confidence',
        'idx_tatums_start', 'key', 'key_confidence', 'loudness', 'mode',
        'mode_confidence', 'start_of_fade_out', 'tempo', 'time_signature',
        'time_signature_confidence', 'track_id', 'analyzer_version',
        'artist_7digitalid', 'artist_familiarity', 'artist_hotttnesss',
        'artist_id', 'artist_latitude', 'artist_location', 'artist_longitude',
        'artist_mbid', 'artist_name', 'artist_playmeid', 'genre',
        'idx_artist_terms', 'idx_similar_artists', 'release',
        'release_7digitalid', 'song_hotttnesss', 'song_id', 'title',
        'track_7digitalid', 'idx_artist_mbtags', 'year'])
        
        file_count = 0
        for dirpath, dirs, files in os.walk("../data/MillionSongSubset"):
            for filename in files:
                file_count += 1

        for filepath in tqdm(walkdir("../data/MillionSongSubset"), total=file_count): # iterate over all existing h5 files
            # for filename in filenames:
                if filepath.endswith(".h5"): # keep only h5 files
                    # finding the h5 file keys
                    # with h5py.File(os.path.join(root, filename), "r") as f:
                    #     print(f.keys())

                    #     for k in f.keys():
                    #         print(f[k].keys())

                    #         for kk in f[k].keys():
                    #             print(f[k][kk])
                    # quit()

                    hdf = pd.HDFStore(filepath, mode="r")
                    temp_df = pd.concat([hdf.get("/analysis/songs/"), hdf.get("/metadata/songs/"), hdf.get("/musicbrainz/songs/")], axis=1)

                    writer.writerow(temp_df.iloc[0])

                    # print(hdf.get("/analysis/songs/"))
                    # print(hdf.get("/metadata/songs/"))
                    # print(hdf.get("/musicbrainz/songs/"))
                    # writer.writerow({'song_name': hdf.get("/metadata/songs/".artist_name), 'artist': hdf.get("/metadata/songs/".title)}) # save song and artist name
                    hdf.close()

def get_artist_names():
    with open("../data/artist_names.csv", "w") as f:
        writer = csv.writer(f) # create the csv writer

        for root, dirnames, filenames in os.walk("../data/MillionSongSubset"): # iterate over all existing h5 files
            for filename in filenames:
                if filename.endswith(".h5"): # keep only h5 files
                    hdf = pd.HDFStore(os.path.join(root, filename), mode="r")
                    writer.writerow(hdf.get("/metadata/songs/").artist_name) # save the artist name
                    hdf.close()

def get_song_and_artist_name():
    file_count = 0
    for dirpath, dirs, files in os.walk("../data/MillionSongSubset"):
        for filename in files:
            file_count += 1

    with open("../data/info_for_spotify_api.csv", "w") as f:
        writer = csv.writer(f) # create the csv writer
        writer.writerow(["song", "artist"])
        
        for filepath in tqdm(walkdir("../data/MillionSongSubset"), total=file_count): # iterate over all existing h5 files
                if filepath.endswith(".h5"): # keep only h5 files
                    hdf = pd.HDFStore(filepath, mode="r")
                    # print(hdf.get("/metadata/songs/").artist_name[0])
                    # print(hdf.get("/metadata/songs/").title[0])
                    writer.writerow([hdf.get("/metadata/songs/").title[0], hdf.get("/metadata/songs/").artist_name[0]])
                    hdf.close()

if __name__ == "__main__":
    # get_all_data()
    # get_artist_names()
    get_song_and_artist_name()
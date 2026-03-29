import pandas as pd
import os

split_nums = [1,2,3,4,5]

final_df = df = pd.DataFrame()


folder = "../data"

for split_num in split_nums:
    lastfm_filename = f"lastfm_train_test_comb-{split_num}.csv"
    spotify_filename = f"lastfm_train_test_comb-{split_num}_spotify_features_data_unclean.csv"

    # read in spotify api collected data & drop song_name, artist_name
    spotify_df = pd.read_csv(os.path.join(folder, spotify_filename))
    spotify_df.drop(['song_name', 'artist_name'], axis=1)

    # only get rows that we have spotify feature data for
    lastfm_df = pd.read_csv(os.path.join(folder, lastfm_filename), nrows=len(spotify_df))

    # merge the two dataframes
    merged_df = pd.concat([lastfm_df, spotify_df], axis=1)

    # keep concatinating to final_df
    if final_df.empty:
        final_df = merged_df
    else:
        final_df = pd.concat([final_df, merged_df])

# save final_df to csv
final_len = len(final_df)

output_filename = f"lastfm_spotify_train_test_comb_{final_len}_entries.csv"
final_df.to_csv(os.path.join(folder, output_filename), index = False)

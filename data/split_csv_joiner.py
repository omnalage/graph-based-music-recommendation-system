import pandas as pd

df = pd.read_csv("lastfm_train_test_comb-1.csv")
df = pd.concat([df, pd.read_csv("lastfm_train_test_comb-2.csv")])
df = pd.concat([df, pd.read_csv("lastfm_train_test_comb-3.csv")])
df = pd.concat([df, pd.read_csv("lastfm_train_test_comb-4.csv")])
df = pd.concat([df, pd.read_csv("lastfm_train_test_comb-5.csv")])
df.to_csv("lastfm_train_test_comb.csv", index = False)
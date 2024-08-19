import pickle

# load pickle as df
file_path = '/Users/olivier/Documents/MSc/thesis/COPBET_Python/Analysis/simulated_df.pkl'
df = pd.read_pickle(file_path)

# save df as pkl pickle 
with open('/Users/olivier/Documents/MSc/thesis/COPBET_Python/Analysis/dataframe_pickle.pkl', 'wb') as f:
    pickle.dump(df, f)
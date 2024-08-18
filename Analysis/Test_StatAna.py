import pandas as pd
from scipy.stats import ttest_rel

# Path to your .pkl file
file_path = '/Users/olivier/Documents/MSc/thesis/COPBET_Python/Analysis/simulated_df.pkl'

# Load the DataFrame
df = pd.read_pickle(file_path)

#df = df.iloc[:, :-3]

# Filter for the basel_LSD dataset
# This line filters the DataFrame to include only rows where the 'dataset' column contains 'basel_LSD'.
# The .apply(lambda x: 'basel_LSD' in x) part checks if 'basel_LSD' is part of each entry in the 'dataset' column.

df['dataset'] = df['dataset'].apply(lambda x: x[0] if isinstance(x, np.ndarray) else x)
df['task'] = df['task'].apply(lambda x: x[0] if isinstance(x, np.ndarray) else x)

lsd_data = df[df['dataset'].apply(lambda x: 'basel_lsd' in x)]

# Further filter for LSD and Placebo conditions
# These lines further filter the 'basel_lsd_data' DataFrame to create two new DataFrames:
# 'lsd_data' for rows where the 'task' column contains 'LSD', and 'placebo_data' for rows with 'Placebo'.
lsd_data = basel_lsd_data[basel_lsd_data['task'].apply(lambda x: 'LSD' in x)]
placebo_data = basel_lsd_data[basel_lsd_data['task'].apply(lambda x: 'Placebo' in x)]

# Ensure the two DataFrames are aligned by subject (just in case they aren't already)
# This step sorts both DataFrames by the 'subject' column and resets the index.
# Sorting and resetting the index ensures that the rows in 'lsd_data' and 'placebo_data' correspond to the same subjects.
lsd_data = lsd_data.sort_values(by='subject').reset_index(drop=True)
placebo_data = placebo_data.sort_values(by='subject').reset_index(drop=True)

# Step 4: Select the column you want to compare (e.g., entropy_metastate)
# Here, we extract the values from the 'entropy_metastate' column for both conditions (LSD and Placebo).
# These values will be used in the paired t-test.
lsd_values = lsd_data['entropy_metastate']
placebo_values = placebo_data['entropy_metastate']

# Step 5: Perform the paired t-test
# The ttest_rel function from scipy.stats is used to perform the paired t-test.
# This test compares the 'entropy_metastate' values between the LSD and Placebo conditions for each subject.
t_stat, p_value = ttest_rel(lsd_values, placebo_values)

# Step 6: Print the results of the paired t-test
# The t-statistic indicates the magnitude of the difference between the two conditions.
# The p-value indicates the statistical significance of the difference. A small p-value (typically ≤ 0.05) indicates strong evidence against the null hypothesis, suggesting that there is a significant difference between the two conditions.
print(f"T-statistic: {t_stat}, P-value: {p_value}")
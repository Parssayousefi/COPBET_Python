import scipy.io
import pandas as pd
import numpy as np


'''

Script to load .mat file containing entropy data and convert it to a pandas DataFrame
- handles different types of columns (single values, 1x100 arrays, 17x17 arrays)

'''
# Load the .mat file
mat = scipy.io.loadmat('/Users/olivier/Documents/MSc/thesis/COPBET_Python/Analysis/tbl_struct.mat')

# Access the structure (the name of the struct is 'tbl_struct')
tbl_struct = mat['tbl_struct']

# Specify the columns to extract
columns_to_extract = [
    'data', 
    'dataset', 
    'subject', 
    'task', 
    'session', 
    'atlas', 
    'conreg', 
    'entropy_metastate', 
    'entropy_LZc', 
    'entropy_pl', 
    'dcc_entropy', 
    'dcc_var'
]

# Initialize a dictionary to hold data
data_dict = {}

# Process each column individually
for col in columns_to_extract:
    print(f"Processing column: {col}")
    
    # Extract the column data from the MATLAB structure and remove unnecessary dimensions
    field_data = tbl_struct[col].squeeze()
    
    # Convert 0-dimensional arrays (single values) to simple scalars
    if isinstance(field_data, np.ndarray) and field_data.ndim == 0:
        field_data = field_data.item()

    # Handle specific cases with separate elif statements
    if col == 'entropy_pl':
        # Preserve 1x100 arrays as they are
        data_dict[col] = [item.squeeze() if isinstance(item, np.ndarray) else item for item in field_data]
        print(f"Processed {col} with nested arrays, first entry shape: {data_dict[col][0].shape}")
    elif col == 'dcc_entropy':
        # Preserve 17x17 arrays as they are
        data_dict[col] = [item for item in field_data]
        print(f"Processed {col} with nested arrays, first entry shape: {data_dict[col][0].shape}")
    elif col == 'dcc_var':
        # Preserve 17x17 arrays as they are
        data_dict[col] = [item for item in field_data]
        print(f"Processed {col} with nested arrays, first entry shape: {data_dict[col][0].shape}")
    else:
        # General case: handle other columns by unwrapping single-element arrays
        data_dict[col] = [item.item() if isinstance(item, np.ndarray) and item.size == 1 else item for item in field_data]

    print(f"Finished processing column: {col}\n")

# Convert the dictionary to a DataFrame
df = pd.DataFrame(data_dict)

# Display the first few rows and the data types of the columns
print(df.head())
print(df.dtypes)
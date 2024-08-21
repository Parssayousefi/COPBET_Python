import scipy.io
import pandas as pd
import numpy as np


'''

Script to load .mat file containing entropy data and convert it to a pandas DataFrame
- handles different types of columns (single values, 1x100 arrays, 17x17 arrays)
- because certain imported columns are squeezed they might become objects that need to be converted to numpy arrays again later
  this is now done already for the entropy_pl column

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
    'dcc_var']

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

# convert entropy_pl object to numpy arrays
df['entropy_pl'] = df['entropy_pl'].apply(lambda x: np.array(x))
# Keep only the first 17 out of 100 columns of df['entropy_pl']
df['entropy_pl'] = df['entropy_pl'].apply(lambda x: x[:, :17]) #if isinstance(x, np.ndarray) and x.ndim == 2 else x)

# check type of array in entropy_pl column
df['entropy_pl'][0].dtype
# check size of array in entropy_pl column
df['entropy_pl'].iloc[0].shape

## remark: when imorting the df as pickle as is done in Test_StataAna_v2.py, 
# the conversion of entropy_pl to numpy array creates a type called f64
# however when converting the column to numpy array from imported mat table, the type is float64
# now this is the same thing but it's interesting that importing the df as pickle or from .mat
# changes certain things and this might be good to keep in mind when working with the data
 
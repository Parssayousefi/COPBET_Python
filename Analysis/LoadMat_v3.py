import scipy.io
import pandas as pd
import numpy as np

# Load the .mat file
mat = scipy.io.loadmat('/Users/olivier/Documents/MSc/thesis/COPBET_Python/Analysis/tbl_struct.mat')

# Access the structure (the name of the struct is 'tbl_struct')
tbl_struct = mat['tbl_struct']

# Specify the columns to extract
columns_to_extract = ['data', 
'dataset', 
'subject', 
'task', 
'session', 
'atlas', 'conreg', 
'entropy_metastate', 
'entropy_LZc', 
'entropy_pl', 
'dcc_entropy', 
'dcc_var']

# Initialize a dictionary to hold data
data_dict = {}

# Process each specified column in the struct because different columns having different shapes and types
# > extract the field and process it accordingly
for col in columns_to_extract:
    print(f"Processing column: {col}")
    
    # Extract the field
    field_data = tbl_struct[col].squeeze()
    
    # If the field_data is a 0-dimensional array, extract its value (convert to scalar)
    if isinstance(field_data, np.ndarray) and field_data.ndim == 0: 
        # because the loadmat function returns a 0-dimensional array for scalar values
        field_data = field_data.item() # extracts the scalar value from a 0-dimensional array and adds scalar value to the dictionary
    
    # Handle cell arrays (nested arrays)
    if isinstance(field_data, np.ndarray) and field_data.dtype == 'O': # check if the field is of type Object,  i.e. a cell array instead of a numeric array
        # Convert cell arrays to a list of unwrapped elements to handle nested arrays
        if col == 'entropy_pl':
            # For 'entropy_pl', we want to keep the nested 1x100 arrays as they are
            data_dict[col] = [item.squeeze() if isinstance(item, np.ndarray) else item for item in field_data]  # Preserve arrays
            print(f"Processed {col} with nested arrays, first entry shape: {data_dict[col][0].shape}")
        elif col == 'dcc_entropy': 
            data_dict[col] = [item for item in field_data]
            print(f"Processed {col} with nested arrays, first entry shape: {data_dict[col][0].shape}")
        elif col == 'dcc_var':
            data_dict[col] = [item for item in field_data]
            print(f"Processed {col} with nested arrays, first entry shape: {data_dict[col][0].shape}")
            # import dcc_entropy and dcc_var as nested arrays, not squeezed because they are 17x17
        else:
            data_dict[col] = [item.item() if isinstance(item, np.ndarray) and item.size == 1 else item for item in field_data]
    elif isinstance(field_data, np.ndarray):
        # Flatten 2D arrays with shape (1066, 1) to (1066,)
        if field_data.ndim == 2 and field_data.shape[1] == 1:
            data_dict[col] = field_data.flatten()
        elif field_data.ndim == 1:
            data_dict[col] = field_data
        else:
            print(f"Skipping column '{col}' with shape {field_data.shape}")
    elif np.isscalar(field_data):
        # Handle scalar values
        data_dict[col] = [field_data] * len(next(iter(data_dict.values()))) if data_dict else [field_data]
    else:
        print(f"Skipping unsupported field '{col}' of type {type(field_data)}")

    print(f"Finished processing column: {col}\n")

# Convert the dictionary to a DataFrame
df = pd.DataFrame(data_dict)

# Display the DataFrame
#print(df)
#print(df.head())
#print(df.dtypes)
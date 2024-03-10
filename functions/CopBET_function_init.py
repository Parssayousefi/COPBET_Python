import pandas as pd

def CopBET_function_init(in_data, **kwargs):
    parallel = kwargs.get('parallel', True)
    keep_data = kwargs.get('keep_data', True)
    nru_specific = kwargs.get('nru_specific', False)
    
    # Assuming `in_data` can be either a DataFrame, a matrix (list of lists), or a string
    if not isinstance(in_data, pd.DataFrame):
        if isinstance(in_data, (list, str)):  # Simple check for matrix or string
            # Convert matrix or string to DataFrame with one entry
            in_data = pd.DataFrame({'in': [in_data]})
        else:
            raise ValueError("Please specify the input data as either a matrix (nxp, n>1),"
                             " or a DataFrame where the FIRST column contains the data"
                             " with a matrix for each row.")
    
    num_workers = 8 if parallel else 0
    
    if keep_data:
        out_data = in_data
    else:
        out_data = pd.DataFrame()
    
    if 'entropy' in in_data.columns and keep_data:
        print('Warning: Overwriting entropy column in data table')
    
    return out_data, num_workers, in_data, nru_specific

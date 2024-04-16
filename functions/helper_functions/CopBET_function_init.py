import pandas as pd

def CopBET_function_init(in_data, **kwargs):
    """
    Initializes a results table and sets options for processing.

    Args:
        in_data (pandas.DataFrame, list, or str): Input data. Can be a DataFrame, a 2D matrix-like object (list of lists), or a string.
        **kwargs: Keyword arguments:
            parallel (bool, optional): Enable parallel processing. Defaults to True.
            keep_data (bool, optional): Retain a copy of input data in the output. Defaults to True.
            nru_specific (bool, optional): Flag for NRU-specific settings. Defaults to False.

    Returns:
        pandas.DataFrame: Output DataFrame (potentially an unmodified copy of the input)
        int: Number of workers for parallel processing
        pandas.DataFrame: The original input DataFrame
        bool: The value of the `nru_specific` flag
    """

    parallel = kwargs.get('parallel', True)
    keep_data = kwargs.get('keep_data', True)
    nru_specific = kwargs.get('nru_specific', False)

    # Input Data Handling
    if not isinstance(in_data, pd.DataFrame):
        if isinstance(in_data, (list, str)):
            # Create DataFrame with a single entry
            in_data = pd.DataFrame({'in': [in_data]})
        else:
            raise ValueError("Input data must be a DataFrame, a matrix (nxp, n>1), or a string, where the FIRST column of the DataFrame contains the data")

    # Parallel Processing Setup
    num_workers = 8 if parallel else 0

    # Output DataFrame Initialization
    if keep_data:
        out_data = in_data.copy()  # Use .copy() to avoid modifying the input
    else:
        out_data = pd.DataFrame()

    # Entropy Column Warning
    if 'entropy' in in_data.columns and keep_data:
        print('Warning: Overwriting entropy column in data table')

    return out_data, num_workers, in_data, nru_specific

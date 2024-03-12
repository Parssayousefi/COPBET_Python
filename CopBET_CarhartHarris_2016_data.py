import os
import numpy as np
import pandas as pd
from scipy.io import loadmat
import nibabel as nib  # Import nibabel for loading nii.gz files

def CopBET_CarhartHarris_2016_data(atlas='yeo7', ts_ROI2ROI='denoised_volumes', data_path='LSDdata/'):
    """
    Loads the CH2016 data structured according to the README file.

    Args:
        atlas (str, optional): Name of the atlas to use. Defaults to 'yeo7'.
        ts_ROI2ROI (str, optional): Type of data ('denoised_volumes' or other). Defaults to 'denoised_volumes'.
        data_path (str, optional): Base path where the data is located. Defaults to 'LSDdata/'.

    Returns:
        pandas.DataFrame: Dataframe containing metadata and file paths (or loaded data, if applicable) 
        list: Placeholder for data, if applicable
        dict: Placeholder for options, if relevant
    """

    possible_atlases = ['AAL90', 'Craddock200', 'HarvardOxford_cort_subcort', 'Lausanne463', 
                        'Schaefer1000', 'Shen268', 'yeo17', 'smith20', 'SchaeferTian232']
    if atlas not in possible_atlases:
        raise ValueError(f'Invalid atlas: {atlas}. Possible options: {possible_atlases}')

    subs = [d for d in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, d)) and d.startswith('sub-')]
    if not subs:
        raise ValueError("No subject directories found in the data path. Check if you're in the right location.")

    conditions = ['ses-PLCB', 'ses-LSD']

    # Initialize DataFrame for efficiency
    column_types = {'data': object, 'rp': object, 'subject': str, 'condition': str, 
                    'session': int, 'num_vols': int, 'entropy': object}
    tbl = pd.DataFrame(index=range(len(subs) * len(conditions) * 2), columns=column_types.keys()) 

    tblcount = 0

    for sub in subs:
        for cond in conditions:
            for ses in [1, 3]:
                sub_folder = os.path.join(data_path, sub) 
                if ts_ROI2ROI == 'denoised_volumes':
                    # Build potential filenames, check existence
                    for potential_ext in ('.nii.gz', '_shortened.nii.gz'):
                        file_path = os.path.join(sub_folder, cond, 'func', f"{sub}_{cond}_task-rest_run-0{ses}_bold{potential_ext}")
                        if os.path.exists(file_path):
                            tbl.at[tblcount, 'data'] = file_path
                            break  
                    else:  
                        raise FileNotFoundError(f"Could not find denoised_volumes file for {sub}, {cond}, session {ses}") 

                else: 
                    data_path = os.path.join(sub_folder,  'ROIdata', atlas, f'{sub}_{cond}_task-rest_run-0{ses}_bold.mat')
                    if os.path.exists(data_path):
                        V_roi = loadmat(data_path)['V_roi']
                        tbl.at[tblcount, 'data'] = V_roi
                        tbl.at[tblcount, 'num_vols'] = V_roi.shape[0]
                    else:
                        raise FileNotFoundError(f"Could not find ROI data file at {data_path}")

                tbl.at[tblcount, 'subject'] = sub
                tbl.at[tblcount, 'condition'] = cond
                tbl.at[tblcount, 'session'] = ses
                tblcount += 1

    # Equality Check (Optimized)
    if ts_ROI2ROI != 'denoised_volumes':
        for h in range(len(tbl)):
            for h2 in range(h + 1, len(tbl)):
                if tbl.iloc[h]['num_vols'] == tbl.iloc[h2]['num_vols']:
                    if np.allclose(tbl.iloc[h]['data'], tbl.iloc[h2]['data']): 
                        raise ValueError(f"Equality issue for {h}-{h2}")

    # Placeholder for data and options
    data = [] 
    opts = []

    return tbl, data, opts

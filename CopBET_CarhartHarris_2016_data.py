import os
import numpy as np
import pandas as pd
from scipy.io import loadmat
import nibabel as nib

def CopBET_CarhartHarris_2016_data(atlas='yeo7', ts_ROI2ROI='denoised_volumes', type='example'):
    """
    Loads the CH2016 data structured according to the README file.
    Args:
        atlas (str, optional): Name of the atlas to use. Defaults to 'yeo7'.
        ts_ROI2ROI (str, optional): Type of data ('denoised_volumes' or other). Defaults to 'denoised_volumes'.
        type (str, optional): Whether to load 'full' dataset or 'example'. Defaults to 'example'. 
    Returns:
        pandas.DataFrame: Dataframe containing metadata and file paths (or loaded data, if applicable).
        list: Placeholder for data, if applicable.
        dict: Placeholder for options, if relevant.
    """
    possible_atlases = ['AAL90', 'Craddock200', 'HarvardOxford_cort_subcort', 'Lausanne463',
                        'Schaefer1000', 'Shen268', 'yeo17', 'smith20', 'SchaeferTian232']
    if atlas not in possible_atlases:
        raise ValueError(f'Invalid atlas: {atlas}. Possible options: {possible_atlases}')
    if type == 'example':
        topfolder = os.path.join(os.getcwd(), 'LSDdata', 'exampledata')  # Path relative to current directory
    elif type == 'full':
        topfolder = os.path.join(os.getcwd(), 'LSDdata')
    else:
        raise ValueError("Please specify whether to load the full dataset ('full') or 'example'")
    subs = [d for d in os.listdir(topfolder) if os.path.isdir(os.path.join(topfolder, d)) and d.startswith('sub-')]
    if not subs:
        raise ValueError("No subject directories found. Check if you're in the right location.")
    conditions = ['ses-PLCB', 'ses-LSD']
    opts = {'subjects': subs}  # Store subject names in opts
    # Table initialization
    tblvarnames = ['data', 'rp', 'subject', 'condition', 'session', 'num_vols', 'entropy']
    tblvartypes = ['object', 'object', 'str', 'str', 'int', 'int', 'object']
    tbl = pd.DataFrame(columns=tblvarnames)  # Create empty DataFrame 
    tblcount = 0
    for sub in subs:
        for cond in conditions:
            for ses in [1, 3]:
                sub_folder = os.path.join(topfolder, sub)
                if ts_ROI2ROI == 'denoised_volumes':
                    for potential_ext in ('.nii.gz', '_shortened.nii.gz'):
                        file_path = os.path.join(sub_folder, cond, 'func', f"{sub}_{cond}_task-rest_run-0{ses}_bold{potential_ext}")
                        if os.path.exists(file_path):
                            tbl.loc[tblcount, 'data'] = file_path  # Use .loc for efficient assignment
                            break
                    else:
                        raise FileNotFoundError(f"Could not find denoised_volumes file for {sub}, {cond}, session {ses}")
                else:
                    data_path = os.path.join(sub_folder, 'ROIdata', atlas, f'{sub}_{cond}_task-rest_run-0{ses}_bold.mat')
                    if os.path.exists(data_path):
                        V_roi = loadmat(data_path)['V_roi']
                        tbl.loc[tblcount, 'data'] = V_roi
                        tbl.loc[tblcount, 'num_vols'] = V_roi.shape[0]
                    else:
                        raise FileNotFoundError(f"Could not find ROI data file at {data_path}")
                tbl.loc[tblcount, 'subject'] = sub
                tbl.loc[tblcount, 'condition'] = cond
                tbl.loc[tblcount, 'session'] = ses
                tblcount += 1
    
    # Equality Check
    if ts_ROI2ROI != 'denoised_volumes':
        for h in range(len(tbl)):  # Outer loop
            for h2 in range(h + 1, len(tbl)):  # Inner loop; starts from h+1
                if tbl['num_vols'][h] == tbl['num_vols'][h2]:  # Compare number of volumes
                    data1 = tbl['data'][h]
                    data2 = tbl['data'][h2]
                    # Note: Assuming your tbl['data'] elements are NumPy arrays or similar
                    if np.linalg.norm(data1 - data2, 'fro') < 1:  # Frobenius norm check
                        error_msg = f"Equality problem for {h}-{h2}"
                        raise ValueError(error_msg)

    data = []  # Placeholder for any data you want to return
    return tbl, data, opts


atlas = 'Schaefer1000'
tbl, data, opts = CopBET_CarhartHarris_2016_data(atlas, 'denoised_volumes', 'example')
print(tbl)
CopBET_time_series_complexity(input_data=tbl, LZtype='LZ78spatial', keepdata=False, parallel=True)


import os
import numpy as np
import pandas as pd
from scipy.io import loadmat

def CopBET_CarhartHarris_2016_data(atlas='yeo7', ts_ROI2ROI='denoised_volumes', data_type='example'):
    if data_type == 'example':
        topfolder = os.path.join(os.getcwd(), 'LSDdata/exampledata/')
    elif data_type == 'full':
        topfolder = os.path.join(os.getcwd(), 'LSDdata/')
    else:
        raise ValueError("Please specify whether to load the 'full' dataset (needs to be downloaded from OpenNeuro and processed using the function LSDdata/LSDdata_ROI.m first) or 'example' with the first placebo and first LSD scan from subject 1")

    possible_atlases = ['AAL90', 'Craddock200', 'HarvardOxford_cort_subcort', 'Lausanne463', 'Schaefer1000', 'Shen268', 'yeo17', 'smith20', 'SchaeferTian232']
    if atlas not in possible_atlases:
        print(possible_atlases)
        raise ValueError('Please input a different atlas name. Possible options above')

    subs = [d for d in os.listdir(topfolder) if os.path.isdir(os.path.join(topfolder, d)) and d.startswith('sub-')]
    if not subs:
        raise ValueError("Please make sure you're standing in the right directory")

    num_mats = len([f for f in os.listdir(os.path.join(topfolder, 'ROIdata/AAL90/')) if f.endswith('.mat')])
    conditions = ['ses-PLCB', 'ses-LSD']

    tbl = pd.DataFrame(columns=['data', 'rp', 'subject', 'condition', 'session', 'num_vols', 'entropy'], index=range(num_mats))

    tblcount = 0

    for sub in subs:
        for cond in conditions:
            for ses in [1, 3]:
                if ts_ROI2ROI == 'denoised_volumes':
                    file_path = f"{sub}/{cond}/func/{sub}_{cond}_task-rest_run-0{ses}_bold.nii.gz"
                    if os.path.exists(file_path):
                        tbl.at[tblcount, 'data'] = file_path
                    else:
                        tbl.at[tblcount, 'data'] = f"{sub}/{cond}/func/{sub}_{cond}_task-rest_run-0{ses}_bold_shortened.nii.gz"
                else:
                    data_path = os.path.join(topfolder, f'ROIdata/{atlas}/{sub}_{cond}_task-rest_run-0{ses}_bold.mat')
                    if os.path.exists(data_path):
                        V_roi = loadmat(data_path)['V_roi']
                        tbl.at[tblcount, 'data'] = V_roi
                        tbl.at[tblcount, 'num_vols'] = V_roi.shape[0]

                tbl.at[tblcount, 'subject'] = sub
                tbl.at[tblcount, 'condition'] = cond
                tbl.at[tblcount, 'session'] = ses

                tblcount += 1

    # Checking for equality issues if ts_ROI2ROI is not 'denoised_volumes'
    if ts_ROI2ROI != 'denoised_volumes':
        for h in range(len(tbl)):
            for h2 in range(h + 1, len(tbl)):
                if tbl.iloc[h]['num_vols'] == tbl.iloc[h2]['num_vols']:
                    if np.linalg.norm(tbl.iloc[h]['data'] - tbl.iloc[h2]['data'], 'fro') < 1:
                        raise ValueError(f"equality problem for {h}-{h2}")

    data = []
    opts = []

    return tbl, data, opts

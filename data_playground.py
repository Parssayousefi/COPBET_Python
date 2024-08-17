import os
import pandas as pd
from scipy.io import loadmat
import numpy as np
import nibabel as nib 
from functions import 

def CopBET_CarhartHarris_2016_data(atlas='yeo7', ts_ROI2ROI='denoised_volumes', data_type='example'):
    possible_atlases = ['AAL90', 'Craddock200', 'HarvardOxford_cort_subcort', 'Lausanne463',
                        'Schaefer1000', 'Shen268', 'yeo17', 'smith20', 'SchaeferTian232']
    if atlas not in possible_atlases:
        raise ValueError(f'Invalid atlas name. Available options: {possible_atlases}')
    
    if data_type == 'example':
        topfolder = os.path.join(os.getcwd(), 'LSDdata', 'exampledata')
    elif data_type == 'full':
        topfolder = os.path.join(os.getcwd(), 'LSDdata')
    else:
        raise ValueError("Specify 'full' for the complete dataset or 'example' for a subset.")
    
    subs = [d for d in os.listdir(topfolder) if os.path.isdir(os.path.join(topfolder, d)) and d.startswith('sub-')]
    if not subs:
        raise FileNotFoundError("No subject directories found. Check your directory location.")
    
    conditions = ['ses-PLCB', 'ses-LSD']
    tbl = pd.DataFrame(columns=['data', 'rp', 'subject', 'condition', 'session', 'num_vols', 'entropy'])
    tblcount = 0
    
    for sub in subs:
        for cond in conditions:
            for ses in [1, 3]:
                session_data_processed = False
                sub_folder = os.path.join(topfolder, sub)
                func_folder = os.path.join(sub_folder, cond, 'func')
                files = glob(os.path.join(func_folder, f"{sub}_{cond}_task-rest_run-0{ses}_bold*"))
                for file in files:
                    if ts_ROI2ROI == 'denoised_volumes' and ('.nii.gz' in file or '_shortened.nii.gz' in file):
                        tbl.loc[tblcount] = [file, None, sub, cond, ses, None, None]
                        tblcount += 1
                        session_data_processed = True
                        break
                if not session_data_processed and ts_ROI2ROI != 'denoised_volumes':
                    mat_file = os.path.join(topfolder, 'ROIdata', atlas, f"{sub}_{cond}_task-rest_run-0{ses}_bold.mat")
                    if os.path.exists(mat_file):
                        data = loadmat(mat_file)['V_roi']
                        tbl.loc[tblcount] = [data, None, sub, cond, ses, data.shape[0], None]
                        tblcount += 1
                    else:
                        raise FileNotFoundError(f"Data file not found: {mat_file}")
    
    if ts_ROI2ROI != 'denoised_volumes':
        for i in range(len(tbl)):
            for j in range(i + 1, len(tbl)):
                if tbl.iloc[i]['num_vols'] == tbl.iloc[j]['num_vols'] and np.linalg.norm(tbl.iloc[i]['data'] - tbl.iloc[j]['data'], 'fro') < 1:
                    raise ValueError(f"Data consistency issue between rows {i} and {j}")

    return tbl, [], {'subjects': subs}




#BIDS
import os
import pandas as pd
from glob import glob
import json

def extract_entities_from_filename(filename):
    """Extract BIDS entities from a filename."""
    entities = {}
    for part in filename.split('_'):
        if '-' in part:
            key, value = part.split('-', 1)
            entities[key] = value.split('.')[0]  # remove extension if present
    return entities

def parse_bids_directory(directory):
    """Parse a BIDS directory structure to collect relevant files and metadata."""
    data_files = glob(os.path.join(directory, '**', '*bold.nii.gz'), recursive=True)
    data_files += glob(os.path.join(directory, '**', '*bold.nii'), recursive=True)  # Uncompressed NIfTI

    records = []
    
    for file_path in data_files:
        entities = extract_entities_from_filename(os.path.basename(file_path))
        if 'sub' not in entities or 'task' not in entities:
            continue  # Skip files that do not meet minimum BIDS requirements for this context
        
        metadata_path = file_path.replace('_bold.nii.gz', '.json').replace('_bold.nii', '.json')
        metadata = {}
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        
        records.append({
            'file_path': file_path,
            'subject': entities.get('sub'),
            'session': entities.get('ses'),
            'task': entities.get('task'),
            'run': entities.get('run'),
            'metadata': metadata
        })
    
    return pd.DataFrame(records)

# Example usage
bids_directory = r"C:\Users\prsyu\OneDrive\Bidlung\University\M.S. Leiden University\M.S. Neuroscience (Research)\Thesis\CopBET\CopBET_Python\nilearn_data\development_fmri"

df = parse_bids_directory(bids_directory)
print(df.head())

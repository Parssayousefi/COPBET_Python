from bids import BIDSLayout
from nilearn import datasets
from nilearn import input_data
from nilearn.interfaces.fmriprep import load_confounds
import os
import pandas as pd
import numpy as np

"""

v8 updates

- Have the function process and output the csv files; moved csv processing within the function
- added flag for save data=False, 
- change the way csv's are outputted; with the content only containing the time series and the title of the file BIDS inspired containing (subject_id, task, session, dataset)
each saved csv consists of all unique combinations of participant+session
- additionally, function returns a dataframe with all the data concatenaded

- ! Change derivatives to true for cluster data, and to false for nilearn data

"""

def process_data_bids(bids_root, strategy, atlas_name, save_path, save_data=False,limit_subjects=False):
    print("BIDS root:", bids_root)
    print("Directories and files at BIDS root:", os.listdir(bids_root))

    atlases = {
        'schaefer400': datasets.fetch_atlas_schaefer_2018(n_rois=400),
        'schaefer1000': datasets.fetch_atlas_schaefer_2018(n_rois=1000),
        "yeo17": datasets.fetch_atlas_yeo_2011()
    }
    if atlas_name not in atlases:
        raise ValueError(f"Atlas not supported. Available options: {', '.join(atlases.keys())}")

    atlas_data = atlases[atlas_name]
    if atlas_name == 'yeo17':
        atlas_filename = atlas_data['thin_17']
    else:
        atlas_filename = atlas_data.maps
    

    layout = BIDSLayout(bids_root, validate=False, derivatives=True, absolute_paths=True)

    masker = input_data.NiftiLabelsMasker(labels_img=atlas_filename, standardize=True, verbose=2)

    subjects = layout.get_subjects()


    if limit_subjects: # alternative option to run the code more quickly, change number of subjects to your preference
        subjects=subjects[:4] # change number to desired number of particpants to preprocess


    all_dfs = []


    for subject_id in subjects:
        sessions = layout.get_sessions(subject=subject_id) or [None] # handle data sets without sessions
        for session in sessions:
            func_files = layout.get(subject=subject_id, session=session, suffix='bold', extension='nii.gz', return_type='filename')
            print(f"Processing subject {subject_id}, session: {session}, found{len(func_files)} functional files")
            if not func_files:
                print(f"No functional files found for subject {subject_id}, session {session}.")
                continue

            for func_file in func_files:

                task = layout.get_metadata(func_file).get('TaskName', 'unknown')
                print(f"TaskName for file {func_file}: {task}")
                if strategy == 'gsr':
                    confounds = load_confounds(func_file, strategy=['global_signal', "high_pass", "wm_csf"])
                elif strategy == 'compcor':
                    confounds = load_confounds(func_file, strategy=['motion', "high_pass", "wm_csf"], motion="basic", compcor='anat_combined', n_compcor='all') # check whether this is correct
                else:
                    raise ValueError(f"Unknown strategy: {strategy}. Available options: gsr, compcor")
                
                time_series = masker.fit_transform(func_file, confounds=confounds[0])
                if time_series.size == 0:
                    print(f"Empty time series for file {func_file}.")
                    continue
                print(f"Time series shape for file {func_file}: {time_series.shape}")

                df = pd.DataFrame(time_series, columns=[f'Region_{i}' for i in range(time_series.shape[1])])
                
                if df.empty:
                    print(f"entries for dataframe are empty for file {func_file}.")
                    continue


                # Create a copy of the dataframe and add additional columns for the final concatenated dataframe 
                final_df = df.copy()
                final_df['Dataset'] = os.path.basename(bids_root) # add dataset name to dataframe
                final_df['Subject'] = subject_id
                final_df['Session'] = session
                final_df['Task'] = task
                all_dfs.append(final_df)


                if save_data:
                    dataset = os.path.basename(bids_root)
                    csv_filename = f"Dat-{dataset}_Sub-{subject_id}_Task-{task}_Session-{session}_Atlas-{atlas_name}.csv" # create filename
                    df.to_csv(os.path.join(save_path, csv_filename), index=False) # save data
                    print(f"Saved data for dataset {dataset} to {csv_filename}")
                

    final_combined_df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame() # concatenate all dataframes   
    return final_combined_df





#### DEFINE PATHS ####

## paths Parsa:
# bids_root = r"C:\Users\prsyu\OneDrive\Bidlung\University\M.S. Leiden University\M.S. Neuroscience (Research)\Thesis\CopBET\CopBET_Python\nilearn_data\development_fmri"

## paths Olivier:

# local paths
bids_root = "/Users/olivier/nilearn_data/development_fmri"
save_path = "/Users/olivier/Documents/MSc/thesis/Analysis"
# cluster paths
# bids_root = r"/home/s1836706/data_pi-michielvanelkm/ascdb/basel_LAM"
# save_path = r"/home/s1836706/data_pi-michielvanelkm/Olivier/preprocessed_csv"



#### CALL FUNCTION ####

strategy = 'compcor'
atlas_name = "yeo17"
results = process_data_bids(bids_root, strategy, atlas_name, save_path, save_data=True, limit_subjects=True)
print(results)
















##### old csv saving code ####

### save as one csv 
if not results.empty and 'Dataset' in results.columns: 
    dataset_name = results['Dataset'].iloc[0]
else:
    dataset_name = "UnknownDataset" 

csv_filename = f"{dataset_name}_preprocessed.csv" # create filename
results.to_csv(os.path.join(save_path, csv_filename), index=False) # save data
print(f"Saved data for dataset {dataset_name} to {csv_filename}")


#### output separate csv files for each participant
if not results.empty and 'Dataset' in results.columns:
    dataset_name = results['Dataset'].iloc[0]
else:
    dataset_name = "UnknownDataset"

for subject_id in results['Subject'].unique(): 
    subject_df = results[results['Subject'] == subject_id] # filter data for each subject
    csv_filename = f"{subject_id}_{dataset_name}_preprocessed.csv" # create filename
    subject_df.to_csv(os.path.join(save_path, csv_filename), index=False) # save data
    print(f"Saved data for subject {subject_id} from {dataset_name} to {csv_filename}")
from bids import BIDSLayout
from nilearn import datasets
from nilearn import input_data
from nilearn.interfaces.fmriprep import load_confounds
import os
import pandas as pd
import numpy as np

"""

v9.2 updates

- time series masked confound extraction works for compcor, scrubbing is included too
- created separate if statements for gsr and compcor when doing time series extraction

- ! Change derivatives to true for cluster data, and to false for nilearn data
- !! Look into changing the framewise displacement when using a different atlas (higher number of regions means frame wise displacement is affected)


"""


def process_data_bids(bids_root, strategy, atlas_name, save_path, save_data=False, limit_subjects=False):
    print("BIDS root:", bids_root)
    print("Directories and files at BIDS root:", os.listdir(bids_root))

    atlases = {
        'schaefer400': datasets.fetch_atlas_schaefer_2018(n_rois=400),
        'schaefer1000': datasets.fetch_atlas_schaefer_2018(n_rois=1000),
        'yeo17': datasets.fetch_atlas_yeo_2011()
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

    if limit_subjects:  # alternative option to run the code more quickly, change number of subjects to your preference
        subjects = subjects[:1]  # change number to desired number of participants to preprocess

    all_dfs = []

    for subject_id in subjects:
        sessions = layout.get_sessions(subject=subject_id) or [None]  # handle data sets without sessions
        for session in sessions:
            func_files = layout.get(subject=subject_id, session=session, suffix='bold', extension='nii.gz', return_type='filename')
            print(f"Processing subject {subject_id}, session: {session}, found {len(func_files)} functional files")
            if not func_files:
                print(f"No functional files found for subject {subject_id}, session {session}.")
                continue

            for func_file in func_files:
                task = layout.get_metadata(func_file).get('TaskName', 'unknown')
                print(f"TaskName for file {func_file}: {task}")
                sample_mask = None
                if strategy == 'gsr':
                    confounds = load_confounds(func_file, strategy=["motion", "global_signal", "high_pass", "wm_csf"],
                                               motion ='basic',
                                               global_signal='basic', # basic for gsr is often sufficient unless specific reasons
                                               scrub=0,
                                               fd_threshold=0.5,
                                               std_dvars_threshold=1.5) 
                elif strategy == 'compcor':
                    confounds, sample_mask = load_confounds(func_file, strategy=['motion', "high_pass", "scrub", "compcor", "wm_csf"],  # using both wm and csf as compcor regressors
                                                            motion="basic",
                                                            compcor='anat_combined',
                                                            n_compcor='all',
                                                            scrub=0,
                                                            fd_threshold=0.5,
                                                            std_dvars_threshold=1.5)  # check whether this is correct # all components = 50 percent of variance explained
                else:
                    raise ValueError(f"Unknown strategy: {strategy}. Available options: gsr, compcor")

                if strategy == 'gsr':
                    time_series = masker.fit_transform(func_file, confounds=confounds[0], sample_mask=sample_mask)

                elif strategy == 'compcor':
                    time_series = masker.fit_transform(func_file, confounds=confounds, sample_mask=sample_mask)

                    
                if time_series.size == 0:
                    print(f"Empty time series for file {func_file}.")
                    continue
                print(f"Time series shape for file {func_file}: {time_series.shape}")

                df = pd.DataFrame(time_series, columns=[f'Region_{i}' for i in range(time_series.shape[1])])

                if df.empty:
                    print(f"Entries for dataframe are empty for file {func_file}.")
                    continue

                # Print DataFrame columns for debugging
                print(f"DataFrame columns: {df.columns}")

                # Create a copy of the dataframe and add additional columns for the final concatenated dataframe 
                final_df = df.copy()
                final_df['Dataset'] = os.path.basename(bids_root)  # add dataset name to dataframe
                final_df['Subject'] = subject_id
                final_df['Session'] = session
                final_df['Task'] = task
                all_dfs.append(final_df)

                if save_data:
                    dataset = os.path.basename(bids_root)
                    csv_filename = f"dat-{dataset}_sub-{subject_id}_task-{task}_ses-{session}_atlas-{atlas_name}_conreg-{strategy}.csv" 
                    df.to_csv(os.path.join(save_path, csv_filename), index=False)  # save data
                    print(f"Saved data for dataset {dataset} to {csv_filename}")

    final_combined_df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()  # concatenate all dataframes
    return final_combined_df


#### DEFINE PATHS ####

## paths Parsa:
# bids_root = r"C:\Users\prsyu\OneDrive\Bidlung\University\M.S. Leiden University\M.S. Neuroscience (Research)\Thesis\CopBET\CopBET_Python\nilearn_data\development_fmri"

## paths Olivier:

# local paths
# bids_root = "/Users/olivier/nilearn_data/development_fmri"
# save_path = "/Users/olivier/Documents/MSc/thesis/Analysis"

# cluster paths
bids_root = r"/home/s1836706/data_pi-michielvanelkm/ascdb/basel_LAM"
save_path = r"/home/s1836706/data_pi-michielvanelkm/Olivier/preprocessed_csv"



#### CALL FUNCTION ####

strategy = 'gsr'
atlas_name = "schaefer1000"
results = process_data_bids(bids_root, strategy, atlas_name, save_path, save_data=True, limit_subjects=True)
print(results)

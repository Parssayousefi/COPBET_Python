from bids import BIDSLayout
from nilearn import datasets
from nilearn import input_data
from nilearn.interfaces.fmriprep import load_confounds
import os
import pandas as pd
import numpy as np

def process_data_bids(bids_root, strategy, atlas_name):
    print("BIDS root:", bids_root)
    print("Directories and files at BIDS root:", os.listdir(bids_root))

    atlases = {
        'schaefer400': datasets.fetch_atlas_schaefer_2018(n_rois=400),
        'schaefer1000': datasets.fetch_atlas_schaefer_2018(n_rois=1000),
        "yeo": datasets.fetch_atlas_yeo_2011()
    }
    if atlas_name not in atlases:
        raise ValueError(f"Atlas not supported. Available options: {', '.join(atlases.keys())}")

    atlas_data = atlases[atlas_name]
    if atlas_name == 'yeo':
        atlas_filename = atlas_data['thin_17']
    else:
        atlas_filename = atlas_data.maps
    
    layout = BIDSLayout(bids_root, validate=False, derivatives=True, absolute_paths=True)

    masker = input_data.NiftiLabelsMasker(labels_img=atlas_filename, standardize=True, verbose=2)

    all_data = []
    subjects = layout.get_subjects()
    for subject_id in subjects:
        sessions = layout.get_sessions(subject=subject_id)
        for session in sessions:
            func_files = layout.get(subject=subject_id, session=session, suffix='bold', extension='nii.gz', return_type='filename')
            func_files = [func_files[0]] # only take the first file for debugging/code creation purposes # comment out in actual analysis
            for func_file in func_files:
                task = layout.get_metadata(func_file).get('TaskName', 'unknown')
                
                if strategy == 'gsr':
                    confounds = load_confounds(func_file, strategy=['global_signal', "high_pass", "wm_csf"])
                elif strategy == 'compcor':
                    confounds = load_confounds(func_file, strategy=['motion', "high_pass", "wm_csf"], motion="basic", compcor='anat_combined', n_compcor='all')
                else:
                    raise ValueError(f"Unknown strategy: {strategy}. Available options: gsr, compcor")
                
                time_series = masker.fit_transform(func_file, confounds=confounds[0])
                df = pd.DataFrame(time_series, columns=[f'Region_{i}' for i in range(time_series.shape[1])])
                df['Subject'] = subject_id
                df['Session'] = session
                df['Task'] = task

                all_data.append(df)
                break # stop after processing first file of first subject # comment out in full analysis

        break # stop after processing first session of first subject # comment out in full analysis    
    final_df = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
    final_df['Dataset'] = os.path.basename(bids_root)
    return final_df


# path parsa
# bids_root = r"C:\Users\prsyu\OneDrive\Bidlung\University\M.S. Leiden University\M.S. Neuroscience (Research)\Thesis\CopBET\CopBET_Python\nilearn_data\development_fmri"

# path olivier
#bids_root = "/Users/olivier/nilearn_data/development_fmri"
bids_root = r"/home/s1836706/data_pi-michielvanelkm/ascdb/basel_LAM"

strategy = 'compcor'
atlas_name = "yeo"

results = process_data_bids(bids_root, strategy, atlas_name)
print(results)

save_path = r"/home/s1836706/data_pi-michielvanelkm/Olivier/csv_attempt_1"
results.to_csv(save_path, index=False)

results_firstsubj = process_data_bids(bids_root, strategy, atlas_name)
print(results_firstsubj)

save_path = r"/home/s1836706/data_pi-michielvanelkm/Olivier/csv_attempt_2"
results_firstsubj.to_csv(save_path, index=False)
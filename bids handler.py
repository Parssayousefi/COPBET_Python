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
        'schaefer400': datasets.fetch_atlas_schaefer_2018( n_rois=400),
        'schaefer1000': datasets.fetch_atlas_schaefer_2018(n_rois=1000),
        "yeo": datasets.fetch_atlas_yeo_2011()
        
    }
   
    if atlas_name not in atlases:
        raise ValueError(f"Atlas not supported. Available options: {', '.join(atlases.keys())}")

    atlas_data = atlases[atlas_name]
    atlas_filename = atlas_data.maps

    # Initialize BIDS Layout with derivatives enabled
    layout = BIDSLayout(bids_root, validate=False, derivatives=True, absolute_paths=True)
    #print("Subjects found:", layout.get_subjects())

    masker = input_data.NiftiLabelsMasker(labels_img=atlas_filename, standardize=True, verbose=2)
    #all_files = layout.get()
    #print("All files found:", all_files)
    all_data = []
    for subject_id in layout.get_subjects()[3]:
        print("Processing subject:", subject_id)
        func_files = layout.get(subject=subject_id, suffix='bold', extension='nii.gz', return_type='filename')
        #print("Functional files found:", func_files)
        # if not func_files:
        #     continue

        func_file = func_files[0]
        # print("func file",func_file)
        # print("func file[0]",func_files[0])
        #confounds_files = layout.get(subject=subject_id, suffix='regressors', extension='tsv', return_type='filename')
        #print("Confounds files found:", confounds_files)
        
        
        # if not confounds_files:
        #     print(f"No confounds file found for subject {subject_id}.")
        #     continue
        if strategy == 'gsr':
            
            confounds = load_confounds(func_file, strategy=['global_signal',"high_pass", "wm_csf"])
            print(type(confounds[0]))
            print(confounds[0].shape)

        elif strategy == 'compcor':
            confounds = load_confounds(func_file, strategy=['motion',"high_pass", "wm_csf"], motion= "basic", compcor='anat_combined', n_compcor='all')
            print(type(confounds[0]))
            print(confounds[0].shape)
        else:
            raise ValueError(f"Unknown strategy: {strategy}", "Available options: gsr, compcor")

        time_series = masker.fit_transform(func_file, confounds=confounds[0])

        df = pd.DataFrame(time_series, columns=[f'Region_{i}' for i in range(time_series.shape[1])])
        df['Subject'] = subject_id

        all_data.append(df)
    return pd.DataFrame() if not all_data else pd.concat(all_data, ignore_index=True)


bids_root = r"/home/s3648540/data_pi-michielvanelkm/ascdb/basel_LAM"

strategy = 'compcor'
atlas_name = 'schaefer400'
#results_yeo = process_data_bids(bids_root, strategy , atlas_name = 'yeo')
results_schaefer400 = process_data_bids(bids_root, strategy, atlas_name)

print(results_schaefer400)

# if results_df.empty:
#     print("No data to display.")
# else:
#     print(results_df.head())


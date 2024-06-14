import os
import numpy as np
import pandas as pd
from bids import BIDSLayout
from nilearn import datasets
from nilearn import input_data
from nilearn.interfaces.fmriprep import load_confounds
import matlab.engine

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
    atlas_filename = atlas_data['maps'] if atlas_name != 'yeo' else atlas_data['thin_17']

    layout = BIDSLayout(bids_root, validate=False, derivatives=True, absolute_paths=True)
    masker = input_data.NiftiLabelsMasker(labels_img=atlas_filename, standardize=True, verbose=2)
    all_data = []

    for subject_id in layout.get_subjects():
        print("Processing subject:", subject_id)
        func_files = layout.get(subject=subject_id, suffix='bold', extension='nii.gz', return_type='filename')
        if not func_files:
            continue
        func_file = func_files[0]

        confounds = load_confounds(func_file, strategy=['global_signal',"high_pass", "wm_csf"] if strategy == 'gsr' else ['motion',"high_pass", "wm_csf"], motion="basic", compcor='anat_combined', n_compcor='all')

        time_series = masker.fit_transform(func_file, confounds=confounds[0])
        df = pd.DataFrame(time_series)
        df['Subject'] = subject_id  # Preserve the subject ID to maintain traceability

        all_data.append(df)

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.columns = [f'Region_{i}' if i < final_df.shape[1] - 1 else 'Subject' for i in range(final_df.shape[1])]
        return final_df
    else:
        return pd.DataFrame()


def process_and_save_to_matlab(df, eng):
    if df.empty:
        print("No data to process.")
        return None

    try:
        # Collect all numerical data from DataFrame assuming it's under columns named 'Region_x'
        data_columns = df.filter(regex='^Region_')
        
        # Convert numerical data columns to a MATLAB double array nested in a cell
        data = matlab.double(data_columns.values.tolist())

        # Create a MATLAB struct with appropriate fields
        # Initialize empty cells for other fields
        mat_struct = eng.struct('data', data, 
                                'rp', eng.cell([[]]), 
                                'subject', eng.cell([[]]), 
                                'condition', eng.cell([[]]), 
                                'session', eng.cell([[]]), 
                                'num_vols', eng.cell([[]]), 
                                'entropy', eng.cell([[]]))

        # Convert the MATLAB struct to a MATLAB table
        mat_table = eng.struct2table(mat_struct, nargout=1) #, AsArray=True)

        return mat_table
    except Exception as e:
        print(f"Failed to create MATLAB table: {str(e)}")
        return None
    
bids_root = r"C:\Users\prsyu\OneDrive\Bidlung\University\M.S. Leiden University\M.S. Neuroscience (Research)\Thesis\CopBET\CopBET_Python\nilearn_data\development_fmri"

strategy = 'compcor'
atlas_name = "schaefer400"

eng = matlab.engine.start_matlab()


results = process_data_bids(bids_root, strategy, atlas_name)
matlab_tbl = process_and_save_to_matlab(results, eng)

try:
    results = process_data_bids(bids_root, strategy, atlas_name)
    matlab_tbl = process_and_save_to_matlab(results, eng)

    save_path = r"C:\Users\prsyu\OneDrive\Bidlung\University\M.S. Leiden University\M.S. Neuroscience (Research)\Thesis\CopBET\CopBET_Python"

    if matlab_tbl:
        eng.save(save_path, 'matlab_tbl')
        print("MATLAB table saved.")
    else:
        print("No table to save.")

finally:
    eng.quit()
    print("MATLAB engine closed.")

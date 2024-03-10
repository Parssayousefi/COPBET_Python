# Function to parcellate CH2016 data from openneuro into atlases in the
# 'Atlases' folder
# Copyright (C) 2023 Anders Stevnhoved Olsen & Drummond E-Wen McCulloch
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.

import os
import numpy as np
import nibabel as nib
import warnings

# Define paths and atlas names
ROIpath = os.path.join(os.getcwd(), 'Atlases')
atlaslocs = [
    'CONN_atlas_2mm.nii',
    'AAL90_2mm.nii',
    'Yeo17_liberal_2mm.nii',
    'Yeo7_2mm.nii',
    'Schaefer1000_2mm',
    'Shen268_2mm.nii',
    'Craddock200_2mm.nii',
    'Lausanne463_2mm.nii',
    'SchaeferTian232_2mm.nii'
]
atlasnames = [
    'HarvardOxford_cort_subcort', 'AAL90', 'yeo17', 'yeo7',
    'Schaefer1000', 'Shen268', 'Craddock200', 'Lausanne463',
    'Smith20', 'SchaeferTian232'
]

# Get list of subjects
subjects = [d for d in os.listdir('LSDdata') if os.path.isdir(os.path.join('LSDdata', d)) and 'sub-' in d]
conditions = ['ses-LSD', 'ses-PLCB']

for subject in subjects:
    for condition in conditions:
        for run in [1, 3]:  # 2 is music
            V_path = f'LSDdata/{subject}/{condition}/func/{subject}_{condition}_task-rest_run-0{run}_bold.nii.gz'
            V = nib.load(V_path).get_fdata()
            V_sz = V.shape

            if V_sz[3] != 217:
                warnings.warn('Wrong number of volumes')

            for atlasloc, atlasname in zip(atlaslocs, atlasnames):
                ROIatlas = nib.load(os.path.join(ROIpath, atlasloc)).get_fdata()
                ROIsz = ROIatlas.shape

                if V_sz[:3] != ROIsz[:3]:
                    raise ValueError('wrong size')

                if ROIatlas.ndim == 3:
                    ROIs = np.unique(ROIatlas[ROIatlas > 0])
                    num_rois = len(ROIs)
                    V_roi = np.full((V_sz[3], num_rois), np.nan)
                    for i, roi in enumerate(ROIs):
                        for t in range(V_sz[3]):
                            tmp = V[..., t]
                            tmp2 = tmp[ROIatlas == roi]
                            V_roi[t, i] = np.nanmean(tmp2[tmp2 != 0])
                elif ROIatlas.ndim == 4:
                    num_rois = ROIsz[3]
                    V_roi = np.full((V_sz[3], num_rois), np.nan)
                    for roi in range(num_rois):
                        for t in range(V_sz[3]):
                            tmp = V[..., t]
                            tmp2 = tmp[ROIatlas[..., roi] > 0]
                            V_roi[t, roi] = np.nanmean(tmp2[tmp2 != 0])

                roi_data_dir = os.path.join(os.getcwd(), 'LSDdata', 'ROIdata', atlasname)
                os.makedirs(roi_data_dir, exist_ok=True)
                roi_data_path = os.path.join(roi_data_dir, f'{subject}_{condition}_task-rest_run-0{run}_bold.mat')
                np.save(roi_data_path, V_roi)

            print(f'Done with {subject}_{condition}_task-rest_run-0{run}_bold.mat')

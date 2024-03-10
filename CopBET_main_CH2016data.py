import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



# Varley script, temporal LZ78
atlas = 'Schaefer1000'
tbl, data, opts = CopBET_CarhartHarris_2016_data(atlas, 'denoised_volumes', 'example')
tbl = CopBET_time_series_complexity(input_data=tbl, LZtype='LZ78spatial', keepdata=False, parallel=True)



# Assuming CopBETtbl is previously defined or is meant to be tbl
tbl['Time_series_complexity_temporal'] = tbl['entropy']

print(tbl['entropy'])

# Plotting the temporal complexity
#plot_boxplots_ch2016(tbl['entropy'], tbl, 'Time series complexity, temporal')

# Varley script, spatial LZ78
tbl, data, opts = CopBET_CarhartHarris_2016_data(atlas, 'ts', 'example')
tbl = copbet_time_series_complexity(tbl, 'LZ78spatial', True, True)

tbl['Time_series_complexity_spatial'] = tbl['entropy']

# Plotting the spatial complexity
#plot_boxplots_ch2016(tbl['entropy'], tbl, 'Time series complexity, spatial')

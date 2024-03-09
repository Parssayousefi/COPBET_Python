
# out = CopBET_time_series_complexity(in,LZtype,keepdata,parallel)
#
# Copenhagen Brain Entropy Toolbox: Time series complexity
# Evaluates time-series complexity as in Varley et al., 2020. Here, the
# input data is hilbert-transformed, then the amplitude of the
# hilbert-transformed time-series is binarised around the mean value. Then,
# depending on whether spatial or temporal lempel-ziv complexity is to be
# computed, the matrix is flattened along one or the other direction. It is
# also possible to use the LZ76 exhaustive algorithm here instead of the
# LZ78 algorithm, which was used originally. The output is normalized by
# the LZ score of a randomly permuted version of the input data. 
#
# Input:
#   in: a matrix (nxp,n>1) or a table where the first column contains
#   matrices (in cells) to be concatenated before clustering, e.g.,
#   different subjects or scan sessions.
#   LZtype: one of 'LZ78spatial','LZ78temporal','LZ76spatial','LZ76temporal'
# name-value pairs:
#   keepdata: Indicates whether the output table also should contain the
#   input data, i.e., by adding an extra column containing entropy values.
#   Defaults to true
#
# Neurobiology Research Unit, 2023
# Please cite McCulloch, Olsen et al., 2023: "Navigating Chaos in
# Psychedelic Neuroimaging: A Rigorous Empirical Evaluation of the Entropic
# Brain Hypothesis" if you use CopBET in your studies. Please read the
# paper to get a notion of our recommendations regarding the use of the
# specific methodologies in the toolbox.

# ASO 9/3-2023

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

import numpy as np
from scipy.signal import hilbert

def CopBET_time_series_complexity(input_data, LZtype, **kwargs):
    # Initialize the output
    out = CopBET_function_init(input_data, **kwargs)

    # Validate LZtype
    valid_types = ['LZ78temporal', 'LZ78spatial', 'LZ76temporal', 'LZ76spatial']
    if LZtype not in valid_types:
        raise ValueError("Please specify which type of time-series complexity measure to use. "
                         "Possible inputs are 'LZ78temporal', 'LZ78spatial', 'LZ76temporal', 'LZ76spatial'")

    # Load data and initialize entropy array
    entropy = np.full(len(input_data), np.nan)
    print('Beginning entropy calculations')
    print(f'Running {LZtype}')

    # Main loop through the input data
    for ses, ts in enumerate(input_data):
        # Hilbert transform the BOLD time series and take the absolute values
        abs_hts = np.abs(hilbert(ts))
        mean_bold = np.mean(abs_hts)
        bin_abs_hts = (abs_hts > mean_bold)

        # Create random time series by shuffling each regional time series
        random_ts = np.empty_like(abs_hts)
        for roi in range(ts.shape[1]):
            np.random.shuffle(abs_hts[:, roi])
            random_ts[:, roi] = abs_hts[:, roi]

        M_rand = (random_ts > mean_bold)

        # Perform complexity calculations
        C = np.empty(ts.shape[1])
        C_rand = np.empty(ts.shape[1])

        if LZtype in ['LZ78temporal', 'LZ76temporal']:
            longts = bin_abs_hts.flatten()
            C = cpr(longts)  # Placeholder for complexity calculation
            long_rand = M_rand.flatten()
            C_rand = cpr(long_rand)  # Placeholder for random complexity calculation

        elif LZtype in ['LZ78spatial', 'LZ76spatial']:
            bin_abs_hts = bin_abs_hts.T
            M_rand = M_rand.T

            longts = bin_abs_hts.flatten()
            C = cpr(longts)  # Placeholder for complexity calculation
            long_rand = M_rand.flatten()
            C_rand = cpr(long_rand)  # Placeholder for random complexity calculation

        # Calculate and store the entropy
        entropy[ses] = np.mean(C / C_rand)

        print(f'Done with session {ses + 1} of {len(input_data)}')

    # Update the output with calculated entropy
    out['entropy'] = entropy
    return out

    
def cpr(string):
 
 '''
 """
    Adapted from Schartner's Python code
    https://github.com/mschart/SignalDiversity/blob/master/LZ_Spectral.py
    """
 Lempel-Ziv-Welch compression of binary input string, e.g. string='0010101'. It outputs the size of the dictionary of binary words.
 '''
 d={}
 w = ''
 for c in string:
  wc = w + c
  if wc in d:
   w = wc
  else:
   d[wc]=wc   
   w = c
 return len(d)


## External function: calc_lz_complexity
#CALC_LZ_COMPLEXITY Lempel-Ziv measure of binary sequence complexity. 
#   This function calculates the complexity of a finite binary sequence,
#   according to the algorithm published by Abraham Lempel and Jacob Ziv in
#   the paper "On the Complexity of Finite Sequences", published in 
#   "IEEE Transactions on Information Theory", Vol. IT-22, no. 1, January
#   1976.  From that perspective, the algorithm could be referred to as 
#   "LZ76".
#   
#   Usage: [C, H] = calc_lz_complexity(S, type, normalize)
#
#   INPUTS:
#   
#   S: 
#   A vector consisting of a binary sequence whose complexity is to be
#   analyzed and calculated.  Numeric values will be converted to logical
#   values depending on whether (0) or not (1) they are equal to 0.
#
#   type: 
#   The type of complexity to evaluate as a string, which is one of:
#       - 'exhaustive': complexity measurement is based on decomposing S 
#       into an exhaustive production process.
#       - 'primitive': complexity measurement is based on decomposing S 
#       into a primitive production process.
#   Exhaustive complexity can be considered a lower limit of the complexity
#   measurement approach proposed in LZ76, and primitive complexity an
#   upper limit.
#
#   normalize:
#   A logical value (true or false), used to specify whether or not the 
#   complexity value returned is normalized or not.  
#   Where normalization is applied, the normalized complexity is 
#   calculated from the un-normalized complexity, C_raw, as:
#       C = C_raw / (L / log2(L))
#   where L is the length of the sequence S.
#
#   OUTPUTS:
#
#   C:
#   The Lempel-Ziv complexity value of the sequence S.
#
#   H:
#   A cell array consisting of the history components that were found in
#   the sequence S, whilst calculating C.  Each element in H consists of a
#   vector of logical values (true, false), and represents
#   a history component.
#
#   gs:
#   A vector containing the corresponding eigenfunction that was calculated
#   which corresponds with S.
#
#
#
#   Author: Quang Thai (qlthai@gmail.com)
#   Copyright (C) Quang Thai 2012



def binary_seq_to_string(S):
    return ''.join(str(int(x)) for x in S)

def calc_lz_complexity(S, type, normalize):
    if not isinstance(S, (list, np.ndarray)):
        raise ValueError("'S' must be a vector")
    if not isinstance(normalize, (bool, np.bool_)):
        raise ValueError("'normalize' must be a scalar")
    if type.lower() not in ['exhaustive', 'primitive']:
        raise ValueError("''type'' parameter is not valid, must be either 'exhaustive' or 'primitive'")
    
    S = np.array(S, dtype=bool)
    normalize = bool(normalize)
    L = len(S)
    gs = np.zeros(L + 1, dtype=int)
    gs[0] = 0

    S_string = binary_seq_to_string(S)
    gs[1] = 1

    for n in range(1, L):
        eigenvalue_found = False
        idx_list = np.arange(gs[n] + 1, n + 1)
        for k in range(int(np.ceil(len(idx_list) / 2))):
            m_upper = idx_list[-k - 1]
            if not S_string[:n].find(S_string[m_upper - 1:n]) >= 0:
                gs[n + 1] = m_upper
                eigenvalue_found = True
                break

            m_lower = idx_list[k]
            if S_string[:n].find(S_string[m_lower - 1:n]) >= 0:
                gs[n + 1] = m_lower - 1
                eigenvalue_found = True
                break
            elif m_upper == m_lower + 1:
                gs[n + 1] = m_lower
                eigenvalue_found = True
                break

        if not eigenvalue_found:
            raise ValueError('Internal error: could not find eigenvalue')

    if type.lower() == 'exhaustive':
        h_i = np.zeros(len(gs), dtype=int)
        h_i_length = 1
        h_prev = 0
        while True:
            k = np.argmax(gs[(h_prev + 2):] > h_prev) + 1
            if k > 0:
                h_i_length += 1
                h_prev += k
                h_i[h_i_length - 1] = h_prev
            else:
                break
    else:
        _, n = np.unique(gs, return_index=True)
        h_i_length = len(n)
        h_i = n - 1

    if h_i[h_i_length - 1] != L:
        h_i_length += 1
        h_i[h_i_length - 1] = L

    H = [S[h_i[k - 1] + 1:h_i[k]] for k in range(1, h_i_length)]

    if normalize:
        C = len(H) / (L / np.log2(L))
    else:
        C = len(H)

    gs = gs[1:]

    return C, H, gs

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

import numpy as np

def binary_seq_to_string(S):
    return ''.join(str(int(x)) for x in S)

def calc_lz_complexity(S, type, normalize):
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
        k = 1
        while k is not None:
            k = np.argmax(gs[(h_prev + 2):] > h_prev) + 1
            if k > 0:
                h_i_length += 1
                h_prev += k
                h_i[h_i_length - 1] = h_prev
            else:
                k = None

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

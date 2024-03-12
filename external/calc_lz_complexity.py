import numpy as np
from math import log2
import re



def calc_lz_complexity(S, complexity_type, normalize):
    # Ensure S is a vector and normalize is a scalar
    if not isinstance(S, np.ndarray) or S.ndim != 1:
        raise ValueError("'S' must be a vector")
    if not isinstance(normalize, (bool, np.bool_)):
        raise ValueError("'normalize' must be a scalar")
    if complexity_type not in ('exhaustive', 'primitive'):
        raise ValueError("''type'' parameter is not valid, must be either 'exhaustive' or 'primitive'")
    
    # Convert S to a logical vector (boolean in Python)
    S = np.asarray(S, dtype=bool)

    # Analyze
    L = len(S)
    gs = np.zeros(L + 1)
    gs[0] = 0  # gs(0) = 0 from the paper
    
    S_string = binary_seq_to_string(S)
    gs[1] = 1  # gs(1) in MATLAB is actually gs(0)

    for n in range(1, L):
        idx_list = list(range(gs[n]+1, n+2))  # MATLAB gs indexing starts at 1
        eigenvalue_found = False
        
        for k in range(ceil(len(idx_list) / 2)):
            m_upper = idx_list[-k]
            m_lower = idx_list[k - 1]
            
            if re.search(S_string[m_upper-1:n], S_string[:n-1]) is None:
                gs[n+1] = m_upper
                eigenvalue_found = True
                break

            if re.search(S_string[m_lower-1:n], S_string[:n-1]) is not None:
                gs[n+1] = m_lower - 1
                eigenvalue_found = True
                break

            if m_upper == m_lower + 1:
                gs[n+1] = m_lower
                eigenvalue_found = True
                break

        if not eigenvalue_found:
            raise Exception('Internal error: could not find eigenvalue')



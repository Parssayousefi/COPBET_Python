import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind

def plot_boxplots_ch2016(entropy, tbl, title):
    LSDsessions = [1, 3]
    
    # Assuming tbl is a pandas DataFrame and contains 'session' and 'condition' columns
    # And assuming entropy values are stored in a column whose name is passed as entropy

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle(title)

    for i, LSDses in enumerate(LSDsessions):
        ax = axes[i]
        # Filter tbl for the current session
        session_tbl = tbl[tbl['session'] == LSDses]
        
        # Plot boxplot and stripplot
        sns.boxplot(x='condition', y=entropy, data=session_tbl, ax=ax)
        sns.stripplot(x='condition', y=entropy, data=session_tbl, color='k', alpha=0.5, ax=ax)

        # Perform t-test between conditions for the current session
        plcbs = session_tbl[session_tbl['condition'] == 'ses-PLCB'][entropy]
        lsds = session_tbl[session_tbl['condition'] == 'ses-LSD'][entropy]
        _, p = ttest_ind(plcbs, lsds)

        ax.set_title(f'Session {LSDses}: p={p:.3f}')
    
    plt.tight_layout()
    plt.show()

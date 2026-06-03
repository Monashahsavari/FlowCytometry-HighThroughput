import numpy as np

# =========================
# IRF CONFIGURATION
# =========================

cutoff_frequency_hz = 1.5e6  # Filter cutoff frequency (Hz)
low_gate = 0.02
up_gate = 0.07

# Folder containing .mat files for IRF construction
IRF_folder_path_mat = r"D:\PhD\Flow cytometry\BD Flow cytometer\Need for speed- measurements\Final measurements- Analysis\150\picoscope\3^-05"


# =========================
# PULSE FITTING ALGORITHM PARAMETERS
# =========================
overlap = 50
window_IRF=80
segment_length=160
iteration_number=30
time_interval= 56e-9
# =========================
# CONVERGENCE / STOPPING CRITERIA
# =========================
threshold=8.8e-05
diff_threshold=1E-7
STD=0.0006
# =========================
# DATA DIRECTORIES
# =========================
#IRF_folder_path_import = r"D:\PhD\Flow cytometry\BD Flow cytometer\Need for speed- measurements\Final measurements- Analysis\150\picoscope"
folder_path = r"D:\PhD\Flow cytometry\BD Flow cytometer\Need for speed- measurements\150+++\150+++\picoscope\3^-03\20230512-0013"
base_directory = r"D:\PhD\Flow cytometry\BD Flow cytometer\Need for speed- measurements\Final measurements- Analysis\mixture of 150,200, and 300\picoscope"

import numpy as np
#correction for the noise
order=5
cutoff = 1.5*10**6   # Cutoff frequency of the filter (Hz)
#gate for 150 nm (0.02 to 0.07)
low_gate=0.02
up_gate=0.07

window_IRF=80
#window_size=40
segment_length=160
iteration_number=7
time_interval=56 * 10 ** -9
max_amplitude=3
# stopping algorithm
#threshold_150=8.434717415934406e-05
threshold=8.037702853720162e-05
#threshold_intralipid=0.00013886661638447994
#standard deviation
#STD_intralipid=0.0007666896873138945
STD=0.0006304204464609041
#STD_150=0.0006336088959402889
diff_threshold=1E-7
overlap=50

# Folder containing the .mat files to make IRF
IRF_folder_path_mat = r"D:\PhD\Flow cytometry\BD Flow cytometer\Need for speed- measurements\Final measurements- Analysis\150\picoscope\3^-05"


#IRF_folder_path_mat = r"D:\PhD\Flow cytometry\BD Flow cytometer\Need for speed- measurements\Final measurements- Analysis\mixture of 150,200, and 300\picoscope\3^-05"
#IRF_folder_path_import = r"D:\PhD\Flow cytometry\BD Flow cytometer\Need for speed- measurements\Final measurements- Analysis\150\picoscope"
IRF_folder_path_import =r"D:\PhD\Flow cytometry\BD Flow cytometer\Need for speed- measurements\Final measurements- Analysis\mixture of 150,200, and 300\picoscope"
root_dir = "D:/PhD/Flow cytometry/BD Flow cytometer/Need for speed- measurements/Final measurements- Analysis/mixture of 150,200, and 300/picoscope"
#folder_path = r"D:\PhD\Flow cytometry\BD Flow cytometer\Need for speed- measurements\150+++\150+++\picoscope\3^-03\20230512-0013"


iteration_rechardson_lucy=3


# final analysis of Algorithm
base_directory = r'D:\PhD\Flow cytometry\BD Flow cytometer\Need for speed- measurements\Final measurements- Analysis\mixture of 150,200, and 300\picoscope'



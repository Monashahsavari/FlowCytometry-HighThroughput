import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import functions as func
import variables as var
from scipy.optimize import curve_fit
import custom_plots as custom
import os

#%%
# reading the files of the measurements
data=func.load_mat_files(var.IRF_folder_path_mat)
Signal =data[0]
time_interval =data[1]
fs = (1 / time_interval[0][0])
Time=np.arange(0,len(Signal)*time_interval*1e+6,time_interval*1e+6)

#%%
# correcting for the background of the signal
Background = np.median(Signal)
Signal_C = Signal - Background
#%%
# Noise correction
filtered_signal=func.butter_lowpass_filter(Signal_C, var.cutoff, fs, var.order)
#%%
# Noise distribution
entries, bin_edges =np.histogram(Signal_C,bins=150, range=(-0.02,0.02))
initial_guess = [2e+6, 0, 0.002]  # Initial guess for amplitude, mean, and standard deviation
params, cov = curve_fit(func.gaussian, bin_edges[:-1], entries,p0=initial_guess)
plt.rcdefaults()
plt.rcParams['agg.path.chunksize'] = 10000
plt.rcParams.update({'font.size': 28,'font.family':'Calibri','font.style':'normal'})
plt.rcParams['axes.linewidth'] = 3
fig, ax = plt.subplots(1, 1,figsize=(12,10),dpi=100)
ax.tick_params(axis='y',direction = 'out',which='major', length=10, width=4, colors='k',
               grid_color='k', grid_alpha=0.5)
ax.tick_params(axis='y',which='minor',direction='out', length=7, width=2, colors='k',
              grid_color='k', grid_alpha=0.5)
ax.tick_params(axis='x',left=True, which='major',direction='out', length=10, width=4, colors='k',
               grid_color='k', grid_alpha=0.5)
ax.tick_params(axis='x',which='minor',direction='out', length=7, width=2, colors='k',
              grid_color='k', grid_alpha=0.5)
ax.plot(bin_edges,func.gaussian(bin_edges,params[0],params[1],params[2]),color='crimson',linewidth=4,label='Gaussian fit')
noise=4*params[2]
ax.axvline(x=noise,color='k',linewidth=4, linestyle='--',label='Noise level')
ax.hist(Signal_C,bins=150, range=(-0.02,0.02),color='navy')
leg = ax.legend(fontsize=32,frameon=False, loc='upper right')
ax.set_xlabel('Amplitude (a.u.)',fontname="Calibri", fontsize=36)
ax.set_ylabel('Counts',fontname="Calibri", fontsize=36)
ax.set_xlim(-0.004, 0.02)
ax.set_ylim(0, 0.2e+8)
plot_path = os.path.join(var.IRF_folder_path_mat, 'histogram_signal.png')
plt.savefig(plot_path,bbox_inches='tight')
print(f'noise={noise}')
print(f'std={params[2]}')

#%%
## Signal and the detected peaks
detected_peaks=func.peak_detector(filtered_signal,Signal_C, threshold=10*noise)
df_detected_peaks = pd.DataFrame(detected_peaks, columns=['Location', 'Amplitude'])
fig, axs = plt.subplots(1, 1,figsize=(12,10))
custom.format_axis(fig, axs, 'time (μs)', 'Intensity (a.u.)', 2400, 2600, -0.01, 0.1, 6, 6, log_y=False, fontsize=26, scientific_y=False)
axs.plot(Signal_C, label='Signal',color='navy')
axs.plot(filtered_signal, label='Signal',color='crimson')
axs.plot(df_detected_peaks['Location'].values,df_detected_peaks['Amplitude'].values,'o',color='r')
plot_path = os.path.join(var.IRF_folder_path_mat, 'detected_peaks.png')
plt.savefig(plot_path)
plt.show()
#%%
print(df_detected_peaks)
plt.hist(df_detected_peaks['Amplitude'].values,range=(0,0.4),bins=100)
plt.show()
#%%
fitted_peaks = []
for peak_location in df_detected_peaks['Location']:
    window=var.window_IRF//8
    if window <= peak_location < len(Signal) - window:
        fitted_params = func.fit_gaussian_to_peak(Signal, peak_location, window)
        if fitted_params is not None:
            fitted_peaks.append(fitted_params)
df_detected_peaks_gussian = pd.DataFrame(fitted_peaks, columns=[ 'Amplitude','Location','width'])
#%%
fig, axs = plt.subplots(1, 1,figsize=(12,10))
custom.format_axis(fig, axs, 'Intensity (a.u.)', 'Count', 0, 0.5, 0, 1600, 6, 6, log_y=False, fontsize=26, scientific_y=False)
plt.hist(df_detected_peaks_gussian['Amplitude'].values,range=(0,0.07),bins=100)
plt.axvline(x=noise,color='red', linewidth=3)
plt.show()
#%%
## Further gating the detected events for calculating the instrument function
gated_peaks = df_detected_peaks[(df_detected_peaks_gussian['Amplitude'] >= var.low_gate) &
                                    (df_detected_peaks_gussian['Amplitude'] <= var.up_gate)]
gated_peaks_median=np.median( df_detected_peaks.loc[gated_peaks.index]['Amplitude'].values)
# Calculate the threshold values
lower_threshold = 0.9 * gated_peaks_median
upper_threshold = 1.1 * gated_peaks_median
fig, axs = plt.subplots(1, 1,figsize=(12,10))
custom.format_axis(fig, axs, 'Intensity (a.u.)', 'Count', 0, 0.2, 0, 20*3200, 6, 6, log_y=False, fontsize=26, scientific_y=False)
plt.hist(df_detected_peaks['Amplitude'].values,bins=200)
plt.axvline(x=var.low_gate,color='red', linewidth=3)
plt.axvline(x=var.up_gate,color='red', linewidth=3)
plt.axvline(x=lower_threshold,color='green', linewidth=3)
plt.axvline(x=upper_threshold,color='green', linewidth=3)
plot_path = os.path.join(var.IRF_folder_path_mat, 'hist_gated_peaks.png')
plt.savefig(plot_path)
plt.show()
#%%
# comparing the IRF with the gaussian function
IRF=func.instrument_function(Signal_C,df_detected_peaks_gussian,var.low_gate,var.up_gate,window_size=var.window_IRF)
x=np.arange(0,var.window_IRF*2,1)
print(len(x))
guess=(1,var.window_IRF,10)
params, cov = curve_fit(func.gaussian, x,IRF,p0=guess)
fig, axs = plt.subplots(1, 1,figsize=(12,10))
custom.format_axis(fig, axs, 'Time/time interval', 'Normalized_intensity', 0, 160, -0.1, 1.1, 6, 6, log_y=False, fontsize=26, scientific_y=False)

plt.plot(x,func.gaussian(x,*params),color='crimson',linewidth=3,label='Gaussian function')
plt.plot(IRF,color='navy',linewidth=3,label='IRF')
plt.legend(loc='upper right', bbox_to_anchor=(1, 1))
plot_path = os.path.join(var.IRF_folder_path_mat, 'comparing_instrument_function.png')
plt.savefig(plot_path)
plt.show()

#%%
# Save DataFrame to Excel
pd.DataFrame(IRF).to_excel(f"{var.IRF_folder_path_mat}/IRF.xlsx", index=False)

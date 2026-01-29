import os
import scipy.io
from scipy.signal import butter, filtfilt
from scipy.optimize import curve_fit
import Peak_decomposition_model as PDM
import pandas as pd
from skimage import restoration
import variables as var
import numpy as np
from scipy.signal import find_peaks
import math

# Function to load and analyze one .mat files
def analyze_mat_files(folder_path):
    # List all .mat files in the folder
    mat_files = [f for f in os.listdir(folder_path) if f.endswith('.mat')]

    if not mat_files:
        print("No .mat files found in the folder.")
        return

    print("MAT files found in the folder:")
    for i, file_name in enumerate(mat_files):
        print(f"{i + 1}: {file_name}")

    # Ask the user which file to analyze
    file_number = int(input("Enter the file number you want to analyze: "))

    if 1 <= file_number <= len(mat_files):
        # Load the selected .mat file
        file_path = os.path.join(folder_path, mat_files[file_number - 1])
        data = scipy.io.loadmat(file_path)

        # Analyze the data
        # Replace this with your analysis code
        return data  # Print or analyze the loaded data
    else:
        print("Invalid file number.")
## analyzing all mat files
def load_mat_files(folder_path):
    signal = []
    # List all files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.mat'):
            # Load the .mat file
            mat_data = scipy.io.loadmat(os.path.join(folder_path, file_name))

            # Assuming the data you want is in a variable called 'data'
            if 'A' in mat_data:
                print(file_name)
                signal.append(replace_inf_with_neighbors(mat_data['A'][:, 0]))
            else:
                print(f"'data' key not found in {file_name}")

    # Concatenate all loaded data into a single array
    signal = np.concatenate(signal, axis=0)
    return signal,mat_data['Tinterval']
## without replacing inf values
def load_files(folder_path):
    signal = []
    # List all files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.mat'):
            # Load the .mat file
            mat_data = scipy.io.loadmat(os.path.join(folder_path, file_name))

            # Assuming the data you want is in a variable called 'data'
            if 'A' in mat_data:
                print(file_name)
                signal.append(mat_data['A'][:, 0])
            else:
                print(f"'data' key not found in {file_name}")

    # Concatenate all loaded data into a single array
    signal = np.concatenate(signal, axis=0)
    return signal,mat_data['Tinterval']

def gaussian(x, amplitude, mean, stddev):
    return amplitude * np.exp(-(x - mean)**2 / (2 * stddev**2))

def peak_detector(filtered_data,data, threshold=0, peak_width=1):
    peaks = []
    location=[]
    Amplitude=[]
    for i in range(peak_width, len(filtered_data) - peak_width):
        if filtered_data[i] > threshold:
            is_peak = True
            for j in range(1, peak_width + 1):
                if filtered_data[i] <= filtered_data[i - j] or filtered_data[i] <= filtered_data[i + j]:
                    is_peak = False
                    break
            if is_peak:
                peaks.append((i, data[i]))
                #location.append(i)
                #Amplitude.append(data[i])
                #np.concatenate(location),np.concatenate(Amplitude)
    return peaks

def replace_inf_with_neighbors(arr):
    for i in range(len(arr)):
        if np.isinf(arr[i]):
            # Find the indices of the neighboring non-inf values
            left_index = i - 1
            right_index = i + 1
            while left_index >= 0 and np.isinf(arr[left_index]):
                left_index -= 1
            while right_index < len(arr) and np.isinf(arr[right_index]):
                right_index += 1

            # Replace inf with the average of neighboring non-inf values
            if left_index >= 0 and right_index < len(arr):
                arr[i] = (arr[left_index] + arr[right_index]) / 2
            elif left_index >= 0:
                arr[i] = arr[left_index]
            elif right_index < len(arr):
                arr[i] = arr[right_index]
    return arr


def replace_inf_with_left(arr):
    is_inf = np.isinf(arr)
    indices = np.where(is_inf)[0]

    # Use cumulative maximum to propagate the last non-inf value
    valid_indices = np.maximum.accumulate(~is_inf * np.arange(len(arr)))
    arr[is_inf] = arr[valid_indices[is_inf]]

    return arr


# Function to replace inf values with Gaussian fit values
def replace_inf_with_gaussian(signal, window_size):
    corrected_signal = np.copy(signal)

    # Identify the indices of the inf values
    inf_indices = np.where(np.isinf(signal))[0]

    # Process each inf value
    for idx in inf_indices:
        # Define the window around the inf value
        start = max(0, idx - window_size)
        end = min(len(signal), idx + window_size)

        # Extract the segment around the inf value
        segment = corrected_signal[start:end]
        x_segment = np.arange(start, end)

        # Create a mask to identify non-inf values
        non_inf_mask = ~np.isinf(segment)

        # Get the x and y values for the non-inf part of the segment
        x_non_inf = x_segment[non_inf_mask]
        y_non_inf = segment[non_inf_mask]

        # Fit a Gaussian to the non-saturated parts of the segment
        try:
            popt, _ = curve_fit(gaussian, x_non_inf, y_non_inf, p0=[1, np.mean(x_non_inf), window_size])

            # Replace the inf values with the Gaussian fit values
            segment_inf_indices = np.where(np.isinf(segment))[0]
            x_inf = x_segment[segment_inf_indices]
            corrected_signal[start:end][segment_inf_indices] = gaussian(x_inf, *popt)
        except RuntimeError:
            # Handle the case where the Gaussian fit fails
            print(f"Gaussian fit failed for inf value at index {idx}")

    return corrected_signal


def butter_lowpass_filter(data, cutoff, fs, order):
    nyq=0.5*fs
    normal_cutoff = cutoff / nyq
    # Get the filter coefficients
    b, a = butter(order, normal_cutoff, btype='low', analog=False)

    padlen = min(len(data) - 1, 3 * max(len(a), len(b)))  # Adjust padlen as needed
    y = filtfilt(b, a, data,padlen=padlen)
    return y


def normalize_signal(signal):
    # Normalize signal to have a maximum of 1
    return signal / np.max(signal)

def baseline_correction(signal):
    # Linear baseline correction
    line = np.linspace(signal[0], signal[-1], len(signal))
    return signal - line
# first averaging and then normalizing
def instrument_function_AN(Signal,detected_peaks,low_gate,up_gate,window_size):
    gated_peaks = detected_peaks[(detected_peaks['Amplitude'] >= low_gate) &
                                    (detected_peaks['Amplitude'] <= up_gate)]
    gated_peaks_median=np.median( detected_peaks.loc[gated_peaks.index]['Amplitude'].values)
    # Calculate the threshold values
    lower_threshold = 0.9 * gated_peaks_median
    upper_threshold = 1.1 * gated_peaks_median

    # Filter peaks based on the amplitude criteria
    selected_peaks = detected_peaks[(detected_peaks['Amplitude'] >= lower_threshold) &
                                    (detected_peaks['Amplitude'] <= upper_threshold)]

    # Remove peaks not meeting the criteria from the original DataFrame
    df_detected_peaks_filtered = detected_peaks.loc[selected_peaks.index]
    # Define a list to store instrument function data
    sum_window=np.zeros(window_size*2+1)
    # Iterate over each peak location in df_detected_peaks_filtered
    event_number=len(df_detected_peaks_filtered['Location'])
    print(f'number of included events is {event_number}')
    for peak_location in df_detected_peaks_filtered['Location']:
        if peak_location>window_size and peak_location<len(Signal)-window_size:
            # Get the index range around the peak
            start_index = peak_location - window_size
            end_index = peak_location + window_size
            # Extract the window of data points around the peak
            window_data = Signal[start_index:end_index + 1]  # Adding 1 to end index to include the endpoint
            sum_window=window_data+sum_window
            # Average the window data and append to averaged signal data
            averaged_signal_data=sum_window/len(df_detected_peaks_filtered['Location'].values)
            # Baseline correction
            corrected_peak = baseline_correction(averaged_signal_data)
            # Normalization
            IRF = normalize_signal(corrected_peak)
        else:
            pass
    return IRF


def find_int_bounds(float_num):
    lower_bound = math.floor(float_num)
    upper_bound = math.ceil(float_num)

    # If the float_num is an integer, both bounds will be the same, so we adjust the upper_bound
    if lower_bound == upper_bound:
        upper_bound += 1

    return lower_bound, upper_bound


# first normalizing and then averaging
def instrument_function(Signal,detected_peaks,low_gate,up_gate,window_size):
    gated_peaks = detected_peaks[(detected_peaks['Amplitude'] >= low_gate) &
                                    (detected_peaks['Amplitude'] <= up_gate)]

    # Remove peaks not meeting the criteria from the original DataFrame
    df_detected_peaks_filtered = detected_peaks.loc[gated_peaks.index]
    # Define a list to store instrument function data
    instrument_function_data = []
    averaged_signal_data = []
    sum_window=np.zeros(window_size*2)
    # Iterate over each peak location in df_detected_peaks_filtered
    event_number=len(df_detected_peaks_filtered['Location'])
    print(f'number of included events is {event_number}')
    for peak_location in df_detected_peaks_filtered['Location']:
        if peak_location>window_size and peak_location<len(Signal)-window_size:
            # Get the index range around the peak
            lower, upper = find_int_bounds(peak_location)
            start_index = lower - window_size+1
            end_index = upper + window_size
            # Extract the window of data points around the peak
            window_data = normalize_signal(Signal[start_index:end_index])  # Adding 1 to end index to include the endpoint
            sum_window=window_data+sum_window
            # Average the window data and append to averaged signal data
    IRF =baseline_correction(sum_window/event_number)
    return IRF


def fit_gaussian_to_peak(signal, peak_location, window_size):
    x_data = np.arange(peak_location - window_size, peak_location + window_size + 1)
    y_data = signal[peak_location - window_size: peak_location + window_size + 1]

    initial_guess = [np.max(y_data), peak_location, window_size / 2]
    try:
        popt, _ = curve_fit(gaussian, x_data, y_data, p0=initial_guess)
        return popt  # Returns the fitted parameters: amplitude, center, width
    except RuntimeError:
        return None


def noise_background (arr):
    #background
    # Step 1: Determine the threshold value
    threshold = 2 * np.min(arr)
    # Step 2: Identify parts of the signal that are below the threshold
    below_threshold_indices = arr < threshold
    y_baseline = arr[below_threshold_indices]
    # Fit a linear model y = mx + c
    x_baseline = np.arange(0, len(y_baseline), 1)
    coefficients = np.polyfit(x_baseline, y_baseline, 1)
    m, c = coefficients
    x_data = np.arange(0, len(arr), 1)
    # Step 4: Generate the fitted baseline
    BC = m * x_data + c
    #noise
    range=(-0.005,0.005)
    bins=100
    entries, bin_edges =np.histogram(arr-BC,range=range,bins=bins)
    initial_guess = [2e+7, 0, 0.002]  # Initial guess for amplitude, mean, and standard deviation
    params, cov = curve_fit(gaussian, bin_edges[:-1], entries,p0=initial_guess,maxfev = 10000)
    return params[2],np.median(BC)


def noise_background (arr):
    #background
    # Step 1: Determine the threshold value
    threshold = 2 * np.min(arr)
    # Step 2: Identify parts of the signal that are below the threshold
    below_threshold_indices = arr < threshold
    y_baseline = arr[below_threshold_indices]
    # Fit a linear model y = mx + c
    x_baseline = np.arange(0, len(y_baseline), 1)
    coefficients = np.polyfit(x_baseline, y_baseline, 1)
    m, c = coefficients
    x_data = np.arange(0, len(arr), 1)
    # Step 4: Generate the fitted baseline
    BC = m * x_data + c
    #noise
    range=(-0.005,0.005)
    bins=100
    entries, bin_edges =np.histogram(arr-BC,range=range,bins=bins)
    initial_guess = [2e+7, 0, 0.002]  # Initial guess for amplitude, mean, and standard deviation
    params, cov = curve_fit(gaussian, bin_edges[:-1], entries,p0=initial_guess)
    return 2*params[2],BC

def process_signal(data,part):
    IRF = np.array(pd.read_excel(f"{var.IRF_folder_path_import}\IRF.xlsx")).flatten()
    prolo_IRF = IRF
    Signal = data[part[0]:part[1]]
    Signal_without_inf = replace_inf_with_neighbors(Signal)
    background = np.median(Signal_without_inf)
    detected_peaks_model = PDM.peak_decomposition(prolo_IRF, Signal, var.overlap, var.threshold, var.diff_threshold,
                                                  var.STD, var.max_amplitude, background, var.iteration_number,
                                                  var.segment_length)
    # Create a DataFrame with titles for amplitude and location
    df_detected_peaks_model = pd.DataFrame(
        {'Location_model': detected_peaks_model[0] + part[0], 'Amplitude_model': detected_peaks_model[1]})
    return df_detected_peaks_model,df_detected_peaks_model






#%% functions for peak decomposition model
import numpy as np
from scipy.optimize import curve_fit


def pad_IRF(IRF, total_length):
    original_length = len(IRF)
    # Calculate padding needed on each side
    pad_size = (total_length - original_length) // 2
    # Pad symmetrically, if odd difference, add the extra pad to the end
    pad_before = pad_size
    pad_after = total_length - original_length - pad_before
    # Use np.pad with constant mode, which by default pads with zeros
    padded_IRF = np.pad(IRF, (pad_before, pad_after), 'constant')
    return padded_IRF


def segment_signal(signal, segment_size, overlap):
    segments = []
    start = 0
    while start + segment_size <= len(signal):
        segments.append(signal[start:start + segment_size])
        start += segment_size - overlap
    return segments


def generate_shifted_values(x, shifts, num_shifts):
    shifted_values = np.zeros((num_shifts, len(x)))
    for i, shift in enumerate(shifts):
        if i < num_shifts:
            shifted_values[i] = np.interp(np.arange(len(x)) + shift, np.arange(len(x)), x)
    return shifted_values



def fit_model_nonlinear(IRF, data, initial_parameters, bounds, number):
    def model(x, *params):
        Peaks = params[:2*number]
        shifts = Peaks[::2]
        amplitudes = Peaks[1::2]
        shifted_values = generate_shifted_values(x, shifts, number)
        B = params[-1]
        # Reshape array1 to have shape (number, 1)
        reshaped_array1 = np.reshape(amplitudes, (number, 1))
        # Tile reshaped_array1 to match the shape of array2
        tiled_array1 = np.tile(reshaped_array1, (1, len(IRF)))
        return np.sum(tiled_array1 * shifted_values, axis=0) + B

    try:
        fitted_values, _ = curve_fit(model, IRF, data, bounds=bounds, p0=initial_parameters, max_nfev=300000)
        fitted_model = model(IRF, *fitted_values)
        return fitted_values, fitted_model
    except ValueError as e:
        print(f"ValueError: {e}")
        print("Initial Parameters:", initial_parameters)
        print("Bounds:", bounds)
        # Optionally return None or some default values
        return None, None
def background (arr):
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
    return np.median(BC)



def fitting_model(IRF, data, threshold, diff_threshold, STD_signal, max_amplitude, max_shift, background,
                  max_iteration):
    bounds = ([-max_shift, 0] * max_iteration + [0], [max_shift, max_amplitude] * max_iteration + [3*background])
    number = 1
    data_residual = data.copy()
    fitted_values = np.zeros(2 * max_iteration + 1)
    previous_stopping_criteria = 1
    noise = 2 * STD_signal
    while number <= max_iteration:
        initial_parameters = []
        for i in range(max_iteration):
            if number > i + 1:
                initial_parameters.extend(fitted_values[2 * i:2 * i + 2])
            else:
                shift = np.argmax(IRF) - np.argmax(data_residual)
                amp = data_residual[np.argmax(data_residual)]
                initial_parameters.extend([shift, amp] if number > i else [0, 0])

        initial_parameters.append(fitted_values[max_iteration * 2] if number > 1 else background)
        previous_fitted_values = fitted_values.copy()

        fitted_values, fitted_model = fit_model_nonlinear(IRF, data, initial_parameters, bounds=bounds, number=number)

        current_stopping_criteria = np.mean(((data - fitted_model) ** 2) / fitted_model)
        final_fitted_values = fitted_values.copy()

        if current_stopping_criteria > threshold:
            number += 1
            data_residual = data - fitted_model

            if previous_stopping_criteria - current_stopping_criteria > diff_threshold:
                final_fitted_values = fitted_values.copy()
            else:
                final_fitted_values = previous_fitted_values
                break

            previous_stopping_criteria = current_stopping_criteria
        else:

            break

    Peaks = final_fitted_values[:-1]

    # Filter Peaks and Amplitude arrays
    nonzero_indices = np.where(Peaks[1::2] != 0)[0]
    Location = Peaks[::2][nonzero_indices]
    Amplitude = Peaks[1::2][nonzero_indices]

    noise_indices = np.where(Amplitude > noise)[0]
    Location_filtered = Location[noise_indices]
    Amplitude_filtered = Amplitude[noise_indices]

    return np.argmax(IRF) - Location_filtered, Amplitude_filtered , fitted_model


def peak_decomposition(IRF, original_signal, overlap, threshold, diff_threshold, STD_signal, max_amplitude, background,
                       max_iteration, IRF_length):
    location = []
    Amplitude = []
    model = []
    data = []
    step_size = IRF_length
    segments = segment_signal(original_signal, step_size, overlap)
    max_shift = (IRF_length) / 2+ overlap

    for i, segment in enumerate(segments):
        loc = []
        Amp = []
        if np.std(segment) > STD_signal * 1.5 and len(segment) == IRF_length and not np.any(np.isinf(segment)):

            result = fitting_model(IRF, segment, threshold, diff_threshold, STD_signal, max_amplitude, max_shift,
                                   background, max_iteration)
            filtered_index = np.where(
                np.logical_and(result[0] < (IRF_length - overlap // 2), result[0] >= (overlap // 2)))
            loc = result[0][filtered_index] + i * (IRF_length - overlap)
            Amp = result[1][filtered_index]
            mo = result[2][overlap // 2:len(segment) - overlap // 2]
            da = segment[overlap // 2:len(segment) - overlap // 2]
        else:
            mo = np.full(len(segment) - overlap, np.nan)
            da = np.full(len(segment) - overlap, np.nan)
        location.append(loc)
        Amplitude.append(Amp)
        model.append(mo)
        data.append(da)
    return (np.concatenate(location), np.concatenate(Amplitude), np.concatenate(model), np.concatenate(data))



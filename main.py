import multiprocessing
import functions as func
import time
import variables as var
import pandas as pd
import matplotlib.pyplot as plt
import os


if __name__ == '__main__':
    # Check if the root directory exists
    if not os.path.isdir(var.root_dir):
        print(f"Error: '{var.root_dir}' is not a valid directory.")
    # Walk through all subdirectories
    for subdir, _, _ in os.walk(var.root_dir):
        if subdir == var.root_dir:
            continue  # Skip the main directory itself
        print(f"Searching in: {subdir}")  # Debug: Print the current directory being searched
        # Extract folder name from the subdirectory path
        folder_name = os.path.basename(subdir)
        # Load MATLAB files in the subdirectory
        data = func.load_files(subdir)[0][:]

        num_parts = 8
        part_size = len(data) // num_parts
        signal_parts = [(i * part_size, (i + 1) * part_size) for i in range(num_parts)]
        signal_parts[-1] = (signal_parts[-1][0], len(data))  # Adjust the last part to include any remaining samples
        print(signal_parts)
        start_time = time.time()
        with multiprocessing.Pool(processes=8) as pool:
             results = pool.starmap(func.process_signal, [(data, part) for part in signal_parts])
        end_time = time.time()
        execution_time = end_time - start_time

        # Combine results from all processes
        combined_df_detected_peaks_model = pd.concat([res[0] for res in results if res[0] is not None])
        measurement_time=len(data)*var.time_interval


        # Save DataFrames to separate sheets in the same Excel file
        metadata = pd.DataFrame({
            'Metadata': ['Measurement_time(s)', 'Rate of Detected Peaks (Model)(1/s)'],
            'Value': [measurement_time, len(combined_df_detected_peaks_model)/measurement_time]})
        # Define the path for the Excel file
        excel_file_path = os.path.join(subdir, f"{folder_name}_data.xlsx")

        # Save both DataFrames to separate sheets in the same Excel file
        with pd.ExcelWriter(excel_file_path) as writer:
            metadata.to_excel(writer, sheet_name='Metadata', index=False)
            combined_df_detected_peaks_model.to_excel(writer, sheet_name='Model Data', index=False)

        plt.hist(combined_df_detected_peaks_model['Amplitude_model'], histtype='step', range=(0, 0.3), bins=100,
                 color='navy',
                 linewidth=3, label='Model')
        plt.xlabel('Amplitude')
        plt.ylabel('Frequency')
        plt.legend(fontsize=12, frameon=False)
        plot_path = os.path.join(subdir, 'histogram_signal.png')
        plt.savefig(plot_path)
        plt.show()






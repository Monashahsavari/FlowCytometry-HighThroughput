import pandas as pd
import functions as func
import os
import variables as var
# Threshold values for amplitude
lower_150_threshold = 0.025  # Adjust as needed
lower_200_threshold = 0.110  # Adjust as needed
lower_300_threshold = 0.225
# Dictionary to store the results
results = {}

# Initialize measurement time
measurement_time = None

# Function to read the specific data from an Excel file
def read_excel_data(file_path, subfolder_name):
    global measurement_time
    try:
        # Read 'Model' sheet
        model_df = pd.read_excel(file_path, sheet_name='Model')
        if 'Amplitude_model' in model_df.columns:
            amplitude_model = model_df['Amplitude_model'].tolist()
            results.setdefault(subfolder_name, {})['Amplitude_model'] = amplitude_model
            Location_model = model_df['Location_model'].tolist()
            results.setdefault(subfolder_name, {})['Location_model'] = Location_model

        # Read 'Metadata' sheet
        metadata_df = pd.read_excel(file_path, sheet_name='Metadata')
        if 'Value' in metadata_df.columns:
            measurement_time = metadata_df['Value'].iloc[0]  # Assuming only one value per sheet
            results.setdefault(subfolder_name, {})['Measurement_time(s)'] = measurement_time
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

# Traverse through all subfolders and files
for root, dirs, files in os.walk(var.base_directory):
    for file in files:
        if file.endswith('.xlsx') or file.endswith('.xls'):
            file_path = os.path.join(root, file)
            subfolder_name = os.path.basename(root)
            read_excel_data(file_path, subfolder_name)

# Create the output Excel file path
output_excel_file = os.path.join(var.base_directory, 'summary.xlsx')

# Export the results to an Excel file
with pd.ExcelWriter(output_excel_file) as writer:
    for subfolder, data in results.items():
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name=subfolder, index=False)

print(f"Summary has been exported to {output_excel_file}")





# Read the Excel file
xls = pd.ExcelFile(output_excel_file)

# List to store results for each sheet
results = []

# Iterate over each sheet
for sheet_name in xls.sheet_names:
    # Read the sheet into a DataFrame
    df = pd.read_excel(output_excel_file, sheet_name=sheet_name)

    # Calculate total count
    total_count = len(df)

    # Calculate total measurement time
    total_measurement_time = df['Measurement_time(s)'].iloc[0]

    # Calculate total count rate above noise
    #total_count_rate = total_count / total_measurement_time

    # Calculate total count rate above noise
    count_above_noise = len(df[df['Amplitude_model'] > lower_150_threshold])
    count_rate_above_noise = count_above_noise / total_measurement_time

    # Calculate count rate for 150
    count_150 = len(df[(df['Amplitude_model'] >= lower_150_threshold) & (df['Amplitude_model'] <= lower_200_threshold)])
    count_rate_150 = count_150 / total_measurement_time
    # Calculate count rate for 200
    count_200 = len(
        df[(df['Amplitude_model'] >= lower_200_threshold) & (df['Amplitude_model'] <= lower_300_threshold)])
    count_rate_200 = count_200 / total_measurement_time
    # Calculate count rate for 300
    count_300 = len(
        df[(df['Amplitude_model'] >= lower_300_threshold) ])
    count_rate_300 = count_300 / total_measurement_time

    # Store the results in a dictionary
    result = {
        'Sheet Name': sheet_name,
        'Total Count': count_above_noise,
        'Total Measurement Time': total_measurement_time,
        'Total Count Rate': count_rate_above_noise,
        f'Count Rate Above [{lower_150_threshold}, {lower_200_threshold}]': count_rate_150,
        f'Count Rate Within [{lower_200_threshold}, {lower_300_threshold}]': count_rate_200,
        f'Count Rate above [{lower_300_threshold}]': count_rate_300
    }

    results.append(result)
# Create the output Excel file path
output_excel_file_2 = os.path.join(var.base_directory, 'results_summary.xlsx')
# Create a DataFrame from the results
result_df = pd.DataFrame(results)


result_df.to_excel(output_excel_file_2, index=False)

print(f"All results have been saved to {output_excel_file_2}")



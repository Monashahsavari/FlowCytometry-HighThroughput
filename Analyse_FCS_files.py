import os
import variables as var
import matplotlib as plt
import pandas as pd
# List to store the results
results = []

# Iterate over all files in the directory
for filename in os.listdir(var.fcs_directory):
    if filename.endswith('.fcs'):
        file_path = os.path.join(var.fcs_directory, filename)
        event_count, total_event_count_rate, filtered_event_count, filtered_event_count_rate, above_threshold_event_count, above_threshold_event_count_rate = get_event_counts_and_rates(file_path, lower_threshold, upper_threshold, above_threshold)
        if event_count is not None:
            dilution_factor = filename[:-4]  # Remove the '.fcs' extension
            results.append({
                'Dilution Factor': dilution_factor,
                'Total Event Count': event_count,
                'Total Event Count Rate': total_event_count_rate,
                'Filtered Event Count': filtered_event_count,
                'Filtered Event Count Rate': filtered_event_count_rate,
                'Above Threshold Event Count': above_threshold_event_count,
                'Above Threshold Event Count Rate': above_threshold_event_count_rate
            })

# Convert the results to a pandas DataFrame
df = pd.DataFrame(results)

# Create the output Excel file path
output_excel_file = os.path.join(var.fcs_directory, 'event_counts_and_rates.xlsx')

# Export the DataFrame to an Excel file
df.to_excel(output_excel_file, index=False)

print(f"Event counts and rates have been exported to {output_excel_file}")

# Plotting the results
plt.figure(figsize=(10, 6))
plt.scatter(df['Dilution Factor'], df['Total Event Count Rate'], color='blue', label='Total Event Count Rate')
plt.scatter(df['Dilution Factor'], df['Filtered Event Count Rate'], color='green', label='Filtered Event Count Rate')
plt.scatter(df['Dilution Factor'], df['Above Threshold Event Count Rate'], color='orange', label='Above Threshold Event Count Rate')

# Add vertical lines for specific files or thresholds
for index, row in df.iterrows():
    plt.axvline(x=index, color='red', linestyle='--', linewidth=0.5)
plt.yscale('log')
# Customizing the plot
plt.xlabel('Dilution Factor')
plt.ylabel('Event Count Rate')
plt.title('Event Count Rates for Each FCS File')
plt.xticks(rotation=90)  # Rotate x-axis labels for better readability
plt.legend()
plt.tight_layout()

# Show the plot
plt.show()

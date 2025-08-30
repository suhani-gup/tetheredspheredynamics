import csv
from collections import defaultdict
import statistics
import matplotlib.pyplot as plt
import os
import re

#parses file name and gets duty cycle and position 
def parse_filename(filepath):
    filename = os.path.basename(filepath)
    match = re.search(r'_dl([0-9_]+)_span([0-9_]+)_dc([0-9]+)\.csv$', filename)
    if not match:
        raise ValueError(f"Filename {filename} does not match expected pattern")
    dl_str = match.group(1)
    span_str = match.group(2)
    dc_str = match.group(3)

    dl = float(dl_str.replace('_', '.'))
    span_raw = float(span_str.replace('_', '.'))

    #convert span to dimensionless units
    span_inches = (span_raw - 3) * 14.5
    span_meters = span_inches * 0.0254
    span = span_meters / 1.5 # final dimensionless span

    duty_cycle = int(dc_str)
    return dl, span, duty_cycle


# base path where all files are stored - from ethan's code
folder_path = r'C:\AWARELab'

# Nested dict: duty_cycle -> position -> list of wind speeds
data = defaultdict(list)

# Iterate all CSV files in folder
for fname in os.listdir(folder_path):
    if fname.endswith('.csv'):
        full_path = os.path.join(folder_path, fname)
        try:
            # call parse_filename function to get position and duty_cycle
            dl, span, duty_cycle = parse_filename(full_path)
        except ValueError:
            print(f"Skipping file with unexpected name format: {fname}")
            continue
        
        #open file to read the wind speed data 
        with open(full_path, mode='r') as f:
            reader = csv.reader(f)
            speeds = []
            for row in reader:
                try:
                    speed = float(row[1])
                    speeds.append(speed)
                except (KeyError, ValueError):
                    # Skip rows with missing or invalid data
                    continue
            if speeds:
                data[duty_cycle].append((dl, span, speeds))

print("\n{:<12} {:<10} {:<10} {:<15} {:<15} {:<20}".format(
    "Duty Cycle", "Downstream Location", "Span", "Mean (m/s)", "Std Dev (m/s)", "Turbulent Intensity"
))
print("-" * 110)
for dc in sorted(data.keys()):
    for dl, span, speeds in sorted(data[dc], key=lambda x: x[1]):
        mean = round(statistics.mean(speeds), 7)
        std = round(statistics.stdev(speeds), 7) if len(speeds) > 1 else 0
        turb_intensity = round(std / mean, 7) if mean != 0 else 0
        print(f"{dc:<12} {dl:<10} {span:<10} {mean:<15} {std:<15} {turb_intensity:<20}")

summary_csv_path = os.path.join(folder_path, "windshaper_datatable.csv")
with open(summary_csv_path, mode='w', newline='') as summary_file:
    writer = csv.writer(summary_file)
    writer.writerow(["Duty Cycle", "Downstream Location", "Span", "Mean (m/s)", "Std Dev (m/s)", "Turbulent Intensity"])

    for dc in sorted(data.keys()):
        for dl, span, speeds in sorted(data[dc], key=lambda x: x[1]):
            mean = round(statistics.mean(speeds), 7)
            std = round(statistics.stdev(speeds), 7) if len(speeds) > 1 else 0
            turb_intensity = round(std / mean, 7) if mean != 0 else 0
            writer.writerow([dc, dl, span, mean, std, turb_intensity])
print(f"\nSummary table saved to: {summary_csv_path}")

# Group data by downstream location → dl -> duty_cycle -> list of (span, speeds)
grouped_by_dl = defaultdict(lambda: defaultdict(list))
for dc in data:
    for dl, span, speeds in data[dc]:
        grouped_by_dl[dl][dc].append((span, speeds))

# Now plot one figure per downstream location
for dl in sorted(grouped_by_dl.keys()):
    plt.figure()
    for dc in sorted(grouped_by_dl[dl].keys()):
        spans = []
        means = []
        stds = []
        for span, speeds in sorted(grouped_by_dl[dl][dc], key=lambda x: x[0]):
            spans.append(span)
            means.append(statistics.mean(speeds))
            stds.append(statistics.stdev(speeds) if len(speeds) > 1 else 0)
        
        plt.errorbar(spans, means, yerr=stds, fmt='o-', capsize=4, label=f'{dc}% duty cycle')
    
    plt.xlabel('Spanwise Position (dimensionless)')
    plt.ylabel('Average Wind Speed (m/s)')
    plt.title(f'Wind Speed Profile at Downstream Location {dl} m')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

plt.show()

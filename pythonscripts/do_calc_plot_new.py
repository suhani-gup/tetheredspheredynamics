import pandas as pd
import statistics
import matplotlib.pyplot as plt
import re
from collections import defaultdict

# Parse sheet name format: "span, downstream, duty cycle" e.g. "1, 2ft, 10%"
def parse_sheet_name(sheet_name):
    # Split by comma
    parts = [part.strip() for part in sheet_name.split(',')]
    if len(parts) != 3:
        raise ValueError(f"Sheet name '{sheet_name}' does not match expected format 'span, downstream, duty cycle'")
    
    span_str, downstream_str, duty_cycle_str = parts

    # Parse span as float (assuming it is numeric, like '1')
    try:
        span = float(span_str)
        #convert span to dimensionless units
        span_inches = (span - 3) * 14.5
        span_meters = span_inches * 0.0254
        span = span_meters / 1.5 # final dimensionless span
    except ValueError:
        raise ValueError(f"Invalid span value in sheet name '{span_str}'")

    # Parse downstream location - if it has units like '2ft', extract number and convert to meters
    downstream_match = re.match(r'([0-9.]+)\s*ft', downstream_str, re.IGNORECASE)
    if downstream_match:
        downstream_ft = float(downstream_match.group(1))
        downstream_m = downstream_ft * 0.3048  # ft to meters
    else:
        # if no units, try to parse directly as float
        try:
            downstream_m = float(downstream_str)
        except ValueError:
            raise ValueError(f"Invalid downstream location value in sheet name '{downstream_str}'")
    
    # Parse duty cycle - remove % sign and convert to int
    duty_cycle_match = re.match(r'(\d+)%', duty_cycle_str)
    if duty_cycle_match:
        duty_cycle = int(duty_cycle_match.group(1))
    else:
        try:
            duty_cycle = int(duty_cycle_str)
        except ValueError:
            raise ValueError(f"Invalid duty cycle value in sheet name '{duty_cycle_str}'")

    return span, downstream_m, duty_cycle


# Path to the Excel workbook
excel_path = r'C:\AWARELab\wind_data.xlsx'

# Read all sheets
xls = pd.ExcelFile(excel_path)
sheet_names = xls.sheet_names

data = defaultdict(list)

for sheet_name in sheet_names:
    try:
        span, downstream_m, duty_cycle = parse_sheet_name(sheet_name)
    except ValueError as e:
        print(f"Skipping sheet '{sheet_name}': {e}")
        continue
    
    df = pd.read_excel(xls, sheet_name=sheet_name, header=None)

    # Skip sheet if empty, has <2 columns, or column 1 is all NaNs
    if df.empty or df.shape[1] < 2 or df.iloc[:, 1].dropna().empty:
        print(f"Skipping sheet '{sheet_name}' due to blank or invalid data.")
        continue

    # Extract speeds as list of floats, drop NaNs
    speeds = df.iloc[:, 1].dropna().astype(float).tolist()
    #print(f"Sheet '{sheet_name}' — speeds: {speeds[:5]}... total: {len(speeds)}")
    
    if speeds:
        data[duty_cycle].append((downstream_m, span, speeds))
        print(f"Added data — Duty: {duty_cycle}%, Downstream: {downstream_m} m, Span: {span}, Count: {len(speeds)}")
    else:
        print(f"Skipping sheet '{sheet_name}' — no valid speeds.")

    continue


# Print summary table header
print("\n{:<12} {:<20} {:<10} {:<15} {:<15} {:<20}".format(
    "Duty Cycle", "Downstream Location (m)", "Span", "Mean (m/s)", "Std Dev (m/s)", "Turbulent Intensity"
))
print("-" * 110)

for dc in sorted(data.keys()):
    for downstream_m, span, speeds in sorted(data[dc], key=lambda x: x[0]):
        mean = round(statistics.mean(speeds), 7)
        std = round(statistics.stdev(speeds), 7) if len(speeds) > 1 else 0
        turb_intensity = round(std / mean, 7) if mean != 0 else 0
        print(f"{dc:<12} {downstream_m:<20} {span:<10} {mean:<15} {std:<15} {turb_intensity:<20}")

# Save summary to CSV
summary_csv_path = r'C:\AWARELab\windshaper_datatable.csv'
with open(summary_csv_path, mode='w', newline='') as summary_file:
    import csv
    writer = csv.writer(summary_file)
    writer.writerow(["Duty Cycle", "Downstream Location (m)", "Span", "Mean (m/s)", "Std Dev (m/s)", "Turbulent Intensity"])

    for dc in sorted(data.keys()):
        for downstream_m, span, speeds in sorted(data[dc], key=lambda x: x[0]):
            mean = round(statistics.mean(speeds), 7)
            std = round(statistics.stdev(speeds), 7) if len(speeds) > 1 else 0
            turb_intensity = round(std / mean, 7) if mean != 0 else 0
            writer.writerow([dc, downstream_m, span, mean, std, turb_intensity])

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
    
    plt.xlabel('Spanwise Position (x/L)')
    plt.ylabel('Average Wind Speed (m/s)')
    plt.title(f'Wind Speed Profile at Downstream Location {dl} m')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

plt.show()\



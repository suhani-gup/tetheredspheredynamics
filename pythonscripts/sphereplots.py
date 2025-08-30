import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# === PARAMETERS FROM YOUR SHEET ===
D = 0.3048  # m (diameter)
rho = 1.1965  # kg/m^3
mu = 1.83e-5  # dynamic viscosity (kg/m·s)
A = np.pi * (D / 2)**2  # frontal area

file_path = r'C:\AWARELab\Test Matrix.xlsx'  

cones_df = pd.read_excel(file_path, sheet_name="New Cones", header=8)
circles_df = pd.read_excel(file_path, sheet_name="New Circles", header=8)


print(cones_df.head())
print(circles_df.head())

# === FUNCTION TO CALCULATE Re AND C_d ===
def calculate_drag(df):
    df['Re'] = (rho * df['Velocity (m/s)'] * D) / mu
    df['C_d'] = df['F_d (N)'] / (0.5 * rho * (df['Velocity (m/s)']**2) * A)
    return df

# === APPLY TO BOTH DATAFRAMES ===
cones_df = calculate_drag(cones_df)
circles_df = calculate_drag(circles_df)

# === PLOT ===
plt.figure(figsize=(10,7))
plt.scatter(cones_df['Re'], cones_df['C_d'], label='Cones', color='blue', marker='o')
plt.scatter(circles_df['Re'], circles_df['C_d'], label='Circles', color='red', marker='s')

plt.xlabel('Reynolds Number')
plt.ylabel('Drag Coefficient $C_d$')
plt.title('Drag Coefficient vs. Reynolds Number')
plt.legend()
plt.grid(True)
plt.show()

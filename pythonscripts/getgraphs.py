import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

# === Load CSV ===
df = pd.read_csv(r'C:\AWARELab\windshaper_datatable.csv')

# === Settings ===
all_duty_cycles = sorted(df['Duty Cycle'].unique())

# Fixed color scale ranges
vmin_velocity = 0
vmax_velocity = 12
vmin_ti = 0
vmax_ti = 2.5

for target_duty in all_duty_cycles:

    target_x_meters = 12.0 * 0.3048  # Downstream location to profile (in ft)

    # === Filter for selected duty cycle ===
    df_duty = df[df['Duty Cycle'] == target_duty]

    # === Get unique x and y positions ===
    x_vals = sorted(df_duty['Downstream Location (m)'].unique())
    x_idx = np.argmin(np.abs(np.array(x_vals) - target_x_meters))
    y_vals = sorted(df_duty['Span'].unique())

    # === Initialize data arrays ===
    velocity_grid = np.zeros((len(x_vals), len(y_vals)))
    ti_grid = np.zeros_like(velocity_grid)

    # === Fill data arrays ===
    for i, x in enumerate(x_vals):
        for j, y in enumerate(y_vals):
            row = df_duty[(df_duty['Downstream Location (m)'] == x) & (df_duty['Span'] == y)]
            if not row.empty:
                velocity_grid[i, j] = row['Mean (m/s)'].values[0]
                ti_grid[i, j] = row['Turbulent Intensity'].values[0]

    # === Interpolate onto finer grid ===
    points = np.array([(x, y) for x in x_vals for y in y_vals])

    # Skip this duty cycle if not enough unique X or Y values
    if len(np.unique(points[:, 0])) < 2 or len(np.unique(points[:, 1])) < 2:
        print(f"Skipping duty cycle {target_duty}% due to insufficient data for interpolation.")
        continue

    velocities = velocity_grid.flatten()
    tis = ti_grid.flatten()

    x_fine = np.linspace(min(x_vals), max(x_vals), 100)
    y_fine = np.linspace(min(y_vals), max(y_vals), 100)
    X_fine, Y_fine = np.meshgrid(x_fine, y_fine, indexing='ij')

    velocity_interp = griddata(points, velocities, (X_fine, Y_fine), method='cubic')
    ti_interp = griddata(points, tis, (X_fine, Y_fine), method='cubic')

    # === Plot ===
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))

    # Velocity field
    c1 = axs[0, 0].pcolormesh(X_fine, Y_fine, velocity_interp, shading='auto',
                              cmap='RdYlBu_r', vmin=vmin_velocity, vmax=vmax_velocity)
    axs[0, 0].set_title(f'Velocity Field at {target_duty}% Duty')
    axs[0, 0].set_xlabel('Downstream Distance [m]')
    axs[0, 0].set_ylabel('Spanwise Position')
    fig.colorbar(c1, ax=axs[0, 0], label='Velocity [m/s]')

    axs[0, 0].set_xticks(x_vals)
    axs[0, 0].set_xticklabels([f"{x:.2f}" for x in x_vals])

    # Velocity profile
    axs[0, 1].scatter(velocity_grid[x_idx], y_vals, color='black')
    axs[0, 1].set_title(f'Velocity Profile at {target_x_meters:.2f} m')
    axs[0, 1].set_xlabel('Velocity [m/s]')
    axs[0, 1].set_ylabel('Spanwise Position')
    axs[0, 1].set_xlim(vmin_velocity, vmax_velocity)

    # Turbulent intensity field
    c2 = axs[1, 0].pcolormesh(X_fine, Y_fine, ti_interp, shading='auto',
                              cmap='RdYlBu_r', vmin=vmin_ti, vmax=vmax_ti)
    axs[1, 0].set_title(f'Turbulence Intensity at {target_duty}% Duty Cycle')
    axs[1, 0].set_xlabel('Downstream Distance [m]')
    axs[1, 0].set_ylabel('Spanwise Position')
    fig.colorbar(c2, ax=axs[1, 0], label='TI [%]')

    axs[1, 0].set_xticks(x_vals)
    axs[1, 0].set_xticklabels([f"{x:.2f}" for x in x_vals])

    # TI profile
    axs[1, 1].scatter(ti_grid[x_idx], y_vals, color='black')
    axs[1, 1].set_title(f'TI Profile at {target_x_meters:.2f} m')
    axs[1, 1].set_xlabel('Turbulence Intensity [%]')
    axs[1, 1].set_ylabel('Spanwise Position (x/L)')
    axs[1, 1].set_xlim(vmin_ti, vmax_ti)

    plt.tight_layout()
    plt.show()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
# --- Config ---
file_path = Path("C:/Users/Aina Ajibola/Desktop/New folder/hot5_temperature_baku_1940_2025.csv")  # Path to the dataset
# --- Load the CSV data ---
df = pd.read_csv(file_path)
# Convert 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'])
# Filter for summer months (June, July, August)
summer_data = df[df['Date'].dt.month.isin([6, 7, 8])].copy()
summer_data['DayOfYear'] = summer_data['Date'].dt.dayofyear
# ---------------- Part 1: Calculate Fixed P90 for Climatology (1981-2010) ----------------
# Filter the climatology period (1981–2010) and compute the fixed P90
summer_1981_2010 = summer_data[(summer_data['Date'].dt.year >= 1981) & (summer_data['Date'].dt.year <= 2010)]
climatology_mean = summer_1981_2010.groupby('DayOfYear')['Temperature (°C)'].mean()
# Given fixed P90 value for summer (JJA) 1981–2010
fixed_p90_value = 28.75  # Updated fixed P90 value
# ---------------- Step 2: Extract Heatwave Days for 2021 ----------------
# Filter data for the year 2021
summer_data_2021 = summer_data[summer_data['Date'].dt.year == 2021].copy()
# Step 1: Mark days exceeding P90
summer_data_2021['Exceeds_P90'] = summer_data_2021['Temperature (°C)'] > fixed_p90_value
# Step 2: Identify heatwave periods (3+ consecutive days above P90)
heatwave_periods = []
heatwave_days_idx = []
exceed_flags = summer_data_2021['Exceeds_P90'].values
# Loop through each day
i = 0
while i < len(exceed_flags):
    if exceed_flags[i]:
        count = 1
        # Count consecutive days above P90
        for j in range(i + 1, len(exceed_flags)):
            if exceed_flags[j]:
                count += 1
            else:
                break
        # If sequence is 3+ days, add all indices to heatwave_periods
        if count >= 3:
            heatwave_periods.append((i, i + count - 1))  # store the range (start, end)
            heatwave_days_idx.extend(range(i, i + count))  # all the days in the heatwave
        i += count  # Skip the checked days
    else:
        i += 1
# Get the heatwave days DataFrame
heatwave_days = summer_data_2021.iloc[heatwave_days_idx]
# ---------------- Plotting ----------------
plt.figure(figsize=(14, 7))
# Plot daily temperature for summer 2021
plt.plot(summer_data_2021['Date'], summer_data_2021['Temperature (°C)'], color='blue', alpha=0.7, label='Temperature (2021)')
# Shade heatwave periods in red
for start, end in heatwave_periods:
    plt.fill_between(summer_data_2021['Date'].iloc[start:end + 1], 
                     summer_data_2021['Temperature (°C)'].iloc[start:end + 1], 
                     color='red', alpha=0.3)
# Plot heatwave days as red dots
plt.scatter(heatwave_days['Date'], heatwave_days['Temperature (°C)'], color='red', zorder=5, label='Heatwave Days')
# Plot the fixed P90 line (green dashed)
plt.axhline(fixed_p90_value, color='green', linestyle='--', label=f'Fixed P90: {fixed_p90_value:.2f} °C')
# Count the total number of heatwave periods
total_heatwaves_2021 = len(heatwave_periods)
# Add labels and title for the plot
plt.title(f'Heatwave Period for Summer 2021 (≥3 Consecutive Days Exceeding Fixed P90)\nTotal Heatwaves: {total_heatwaves_2021}', fontsize=16)
plt.xlabel('Date')
plt.ylabel('Temperature (°C)')
# Add a legend with the total number of heatwaves
plt.legend(loc='upper left')
# Format x-axis for better readability
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
plt.gcf().autofmt_xdate()
# Show the plot
plt.tight_layout()
plt.show()
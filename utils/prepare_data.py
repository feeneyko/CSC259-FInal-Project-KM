import os
import pandas as pd

# Read the color matching functions
cie_xyz = pd.read_csv(os.path.join('data', 'CIE_xyz_1931_2deg.csv'))

# Read the K and S data
ks_data = pd.read_csv(os.path.join('data', 'k_and_s_Yoshi_data.csv'))

# Read the illuminant data (D65)
illuminant = pd.read_csv(os.path.join('data', 'CIE_std_illum_D65.csv'))

# Ensure all data covers the same wavelength range and intervals
# Merge the data frames on 'wavelength'
data = pd.merge(ks_data, cie_xyz, on='wavelength', how='inner')
data = pd.merge(data, illuminant, on='wavelength', how='inner')

# Ensure the 'data' directory exists
os.makedirs('data', exist_ok=True)

# Save the prepared data to the 'data' directory
data.to_csv(os.path.join('data', 'prepared_data.csv'), index=False)
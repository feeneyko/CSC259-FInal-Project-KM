import numpy as np
import pandas as pd
from scipy.integrate import trapz
from scipy.interpolate import interp1d

# Load CMF data for x_bar, y_bar, z_bar
x_bar_data = pd.read_csv('x_bar.csv')  # Load x_bar CSV file with wavelength and function value
y_bar_data = pd.read_csv('y_bar.csv')  # Load y_bar CSV file
z_bar_data = pd.read_csv('z_bar.csv')  # Load z_bar CSV file

# Load D65 illuminant data
D65_data = pd.read_csv('D65.csv')  # Load D65 CSV file with wavelength and illuminant values

# Define the common wavelength range (e.g., 380 to 750 nm in steps of 1 nm)
wavelengths = np.linspace(380, 750, 100)  # Adjust if a finer grid is available

# Interpolate CMF and illuminant data to match the common wavelength range
# x_bar_interp = interp1d(x_bar_data['wavelength'], x_bar_data['value'], kind='linear', fill_value="extrapolate")
# y_bar_interp = interp1d(y_bar_data['wavelength'], y_bar_data['value'], kind='linear', fill_value="extrapolate")
# z_bar_interp = interp1d(z_bar_data['wavelength'], z_bar_data['value'], kind='linear', fill_value="extrapolate")
# D65_interp = interp1d(D65_data['wavelength'], D65_data['value'], kind='linear', fill_value="extrapolate")

# Calculate interpolated values for each wavelength
# x_bar = x_bar_interp(wavelengths)
# y_bar = y_bar_interp(wavelengths)
# z_bar = z_bar_interp(wavelengths)
# D65 = D65_interp(wavelengths)

# Define the initial reflectance spectrum R_mix(c, lambda) (Replace with actual data or calculations)
R_mix = np.array([...])  # Replace with actual reflectance data or calculations

# Saunderson coefficients
k1 = 0.1  # Example coefficient, replace with actual values
k2 = 0.2  # Example coefficient, replace with actual values

# Calculate the modified reflectance spectrum using Saunderson’s equation
R_mix_prime = ((1 - k1) * (1 - k2) * R_mix) / (1 - k2 * R_mix)

# Calculate the integrals for X(c), Y(c), Z(c) using the trapezoidal rule
X_c = trapz(x_bar * D65 * R_mix_prime, wavelengths)
Y_c = trapz(y_bar * D65 * R_mix_prime, wavelengths)
Z_c = trapz(z_bar * D65 * R_mix_prime, wavelengths)

# Output the results
print(f'X(c): {X_c}')
print(f'Y(c): {Y_c}')
print(f'Z(c): {Z_c}')

import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import pandas as pd

# Load data
data = pd.read_csv('data/LEGACY_prepared_data.csv')
wavelengths = data['wavelength'].values
# Extract color matching functions and illuminant data
x_bar = data['x_bar'].values
y_bar = data['y_bar'].values
z_bar = data['z_bar'].values
I = data['power'].values

# Equal wavelength intervals
delta_lambda = wavelengths[1] - wavelengths[0]

# Function to apply inverse gamma correction
def inverse_gamma_correct(c):
    if c <= 0.04045:
        return c / 12.92
    else:
        return ((c + 0.055) / 1.055) ** 2.4

# Function to convert sRGB to linear RGB
def srgb_to_linear(srgb):
    return np.array([inverse_gamma_correct(c / 255) for c in srgb])

# Function to convert linear RGB to XYZ
def linear_rgb_to_xyz(rgb):
    M = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    return np.dot(M, rgb)

# Function to convert XYZ to xy chromaticity coordinates
def xyz_to_xy(XYZ):
    X, Y, Z = XYZ
    sum_xyz = X + Y + Z
    if sum_xyz == 0:
        return 0, 0
    x = X / sum_xyz
    y = Y / sum_xyz
    return x, y

# Function to compute XYZ for a wavelength (simplified)
def get_XYZ_from_wavelength(wl):
    # Create interpolation functions for CMFs and illuminant
    x_bar_interp = interp1d(wavelengths, x_bar, kind='linear', bounds_error=False, fill_value=0.0)
    y_bar_interp = interp1d(wavelengths, y_bar, kind='linear', bounds_error=False, fill_value=0.0)
    z_bar_interp = interp1d(wavelengths, z_bar, kind='linear', bounds_error=False, fill_value=0.0)
    I_interp = interp1d(wavelengths, I, kind='linear', bounds_error=False, fill_value=0.0)
    
    # Interpolate CMFs and illuminant at the wavelength wl
    x_bar_wl = x_bar_interp(wl)
    y_bar_wl = y_bar_interp(wl)
    z_bar_wl = z_bar_interp(wl)
    I_wl = I_interp(wl)
    
    # Compute XYZ components
    X = I_wl * x_bar_wl
    Y = I_wl * y_bar_wl
    Z = I_wl * z_bar_wl
    
    return np.array([X, Y, Z])

def plot_chromaticity_diagram_boundary(ax):
    # Load or compute the spectral locus boundary points
    wavelengths = np.linspace(380, 730, 100)
    boundary_xy = []

    for wl in wavelengths:
        # Compute XYZ values for each wavelength (requires color matching functions)
        X, Y, Z = get_XYZ_from_wavelength(wl)
        x, y = xyz_to_xy([X, Y, Z])
        boundary_xy.append([x, y])

    boundary_xy = np.array(boundary_xy)
    ax.plot(boundary_xy[:, 0], boundary_xy[:, 1], 'k')

# Example input sRGB colors
srgb1 = [40, 9, 14]  # Pure red
srgb2 = [61, 42, 47]  # Pure green

# Convert to linear RGB
rgb1_linear = srgb_to_linear(srgb1)
rgb2_linear = srgb_to_linear(srgb2)

# Convert linear RGB to XYZ
xyz1 = linear_rgb_to_xyz(rgb1_linear)
xyz2 = linear_rgb_to_xyz(rgb2_linear)

# Convert XYZ to xy chromaticity coordinates
xy1 = xyz_to_xy(xyz1)
xy2 = xyz_to_xy(xyz2)

# Plot the chromaticity diagram
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(-0.1, 0.8)
ax.set_ylim(-0.1, 0.9)
ax.set_title('CIE 1931 Chromaticity Diagram')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_aspect('equal', adjustable='box')  # Ensures equal scaling for x and y axes

# Plot the boundary
plot_chromaticity_diagram_boundary(ax)

# Plot the points
ax.scatter(*xy1, color=np.array(srgb1)/255, label=f'Color 1: {srgb1}')
ax.scatter(*xy2, color=np.array(srgb2)/255, label=f'Color 2: {srgb2}')


ax.legend()
plt.grid(True)
plt.show()

# Calculate the Reflectance based on Scattering and Absorption
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# Pigment mappings
pigment_mapping = {
    'White': 'white',
    'Black': 'black',
    'Cobalt Blue': 'cobalt b',
    'Quinacridone Magenta': 'quinacridone Magenta',
    'Phthalo Blue (Green Shade)': 'phthalo blue (green shade)',
    'Hansa Yellow': 'hansa Yellow',
    'Phthalo Green': 'phthalo Green',
    'Pyrrole Red': 'pyrrole Red',
    'Ultramarine Blue': 'ultramarine Blue',
    'Dioxazine Purple': 'dioxazine Purple',
    'Pyrrole Orange': 'pyrrole Orange'
}

# Load data
data = pd.read_csv('data/prepared_data.csv')
wavelengths = data['wavelength'].values
# Extract color matching functions and illuminant data
x_bar = data['x_bar'].values
y_bar = data['y_bar'].values
z_bar = data['z_bar'].values
I = data['power'].values

# Equal wavelength intervals
delta_lambda = wavelengths[1] - wavelengths[0]

def gamma_correct(c):
    return pow(np.clip(c, 0, 1), 1 / 2.2)

# Function to convert XYZ to sRGB
def xyz_to_srgb(XYZ):
    X, Y, Z = XYZ
    # sRGB conversion matrix
    M = np.array([[3.2406, -1.5372, -0.4986],
                  [-0.9689,  1.8758,  0.0415],
                  [0.0557, -0.2040,  1.0570]])
    
    # Convert XYZ to linear RGB
    RGB_lin = np.dot(M, [X, Y, Z])

    # Gamma correction
    RGB = [gamma_correct(c) for c in RGB_lin]

    return np.clip(RGB, 0, 1)

def compute_mixture_xyz(pigment_names, proportions):
    # Ensure proportions sum to 1
    proportions = np.array(proportions)
    proportions = proportions / proportions.sum()

    # Initialize K_mix and S_mix as float arrays
    K_mix = np.zeros_like(data['wavelength'].values, dtype=float)
    S_mix = np.zeros_like(data['wavelength'].values, dtype=float)

    # Sum K and S values weighted by proportions
    for pigment_name, proportion in zip(pigment_names, proportions):
        pigment_key = pigment_mapping[pigment_name]
        K = data['k ' + pigment_key].values
        S = data['s ' + pigment_key].values
        K_mix += proportion * K
        S_mix += proportion * S

    # Compute K/S ratio
    ks_ratio = K_mix / S_mix

    # Compute reflectance R(λ) using Kubelka-Munk theory
    ks_ratio = np.maximum(ks_ratio, 0)
    Q = np.sqrt(ks_ratio * (ks_ratio + 2))
    R_inf = 1 + ks_ratio - Q
    R_inf = np.clip(R_inf, 0, 1)

    # Compute the XYZ tristimulus values
    X_num = np.sum(R_inf * I * x_bar) * delta_lambda
    Y_num = np.sum(R_inf * I * y_bar) * delta_lambda
    Z_num = np.sum(R_inf * I * z_bar) * delta_lambda

    # Normalization factor
    Y_norm = np.sum(I * y_bar) * delta_lambda

    # Normalize XYZ values
    X = X_num / Y_norm
    Y = Y_num / Y_norm
    Z = Z_num / Y_norm

    XYZ = [X, Y, Z]

    return XYZ

def XYZ_to_xy(xyz):
    # Normalize XYZ values
    x_val, y_val, z_val = xyz
    sum_xyz = x_val + y_val + z_val
    if sum_xyz == 0:
        return 0, 0
    x = x_val / sum_xyz
    y = y_val / sum_xyz

    return x, y

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
        x, y = XYZ_to_xy([X, Y, Z])
        boundary_xy.append([x, y])

    boundary_xy = np.array(boundary_xy)
    ax.plot(boundary_xy[:, 0], boundary_xy[:, 1], 'k')

# Function to generate mixtures and plot the color gamut
def plot_color_gamut(pigment_names):
    # Generate all combinations of proportions that sum to 1
    resolution = 21  # Adjust for finer granularity
    num_pigments = len(pigment_names)

    if num_pigments == 2:
        fractions = np.linspace(0, 1, resolution)
        sRGB_list = []

        for f in fractions:
            proportions = [f, 1 - f]
            sRGB = xyz_to_srgb(compute_mixture_xyz(pigment_names, proportions))
            sRGB_list.append(sRGB)

        # Plot the colors
        plt.figure(figsize=(12, 2))
        color_array = np.array([sRGB_list])
        plt.imshow(color_array, extent=[0, 1, 0, 0.1])
        plt.xlabel(f'Fraction of {pigment_names[0]}')
        plt.yticks([])
        plt.xticks(fractions, [f"{f:.2f}" for f in fractions], rotation=45)
        plt.title(f"Color Gamut of Mixture: {pigment_names[0]} and {pigment_names[1]}")
        plt.show()

    elif num_pigments == 3:
        # Create a triangular grid of proportions
        ternary_points = []
        sRGB_list = []

        for i in range(resolution):
            for j in range(resolution - i):
                k = resolution - i - j - 1
                proportions = [i / (resolution - 1), j / (resolution - 1), k / (resolution - 1)]
                sRGB = xyz_to_srgb(compute_mixture_xyz(pigment_names, proportions))
                ternary_points.append(proportions)
                sRGB_list.append(sRGB)

        # Prepare data for plotting
        ternary_points = np.array(ternary_points)
        sRGB_list = np.array(sRGB_list)

        # Plotting the color gamut in 2D
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111)

        # Convert ternary coordinates to Cartesian for plotting
        x_coords = 0.5 * (2 * ternary_points[:, 1] + ternary_points[:, 2]) / (ternary_points.sum(axis=1))
        y_coords = (np.sqrt(3) / 2) * ternary_points[:, 2] / (ternary_points.sum(axis=1))

        ax.scatter(x_coords, y_coords, c=sRGB_list, s=50)

        # Set labels and titles
        ax.set_xlabel(f'{pigment_names[1]}')
        ax.set_ylabel(f'{pigment_names[2]}')
        plt.title(f"Color Gamut of Mixture: {', '.join(pigment_names)}")
        ax.set_xticks([])
        ax.set_yticks([])
        plt.show()

    elif num_pigments == 4:
        fractions = np.linspace(0, 1, resolution)
        sRGB_list = []
        xy_list = []

        for p1 in fractions:
            for p2 in fractions:
                for p3 in fractions:
                    if p1 + p2 + p3 <= 1:
                        p4 = 1 - p1 - p2 - p3
                        proportions = [p1, p2, p3, p4]
                        XYZ = compute_mixture_xyz(pigment_names, proportions)
                        sRGB = xyz_to_srgb(XYZ)
                        sRGB_list.append(sRGB)
                        
                        # Convert XYZ to xy chromaticity coordinates
                        x, y = XYZ_to_xy(XYZ)
                        xy_list.append([x, y])

        # Convert lists to numpy arrays
        xy_points = np.array(xy_list)
        sRGB_list = np.array(sRGB_list)

        # Plotting the chromaticity diagram
        fig, ax = plt.subplots(figsize=(8, 8))

        # Set background color to grey
        ax.set_facecolor('grey')

        ax.scatter(xy_points[:, 0], xy_points[:, 1], c=sRGB_list, s=50)

        # Set labels and titles
        ax.set_xlabel('x chromaticity coordinate')
        ax.set_ylabel('y chromaticity coordinate')
        plt.title(f"Chromaticity Diagram of Mixture: {', '.join(pigment_names)}")

        # Optionally, plot the CIE 1931 chromaticity diagram boundary
        plot_chromaticity_diagram_boundary(ax)

        plt.show()

    else:
        print("Mixing more than 4 pigments is complex to visualize. Please select up to 4 pigments.")

# Example usage:

# Mix two pigments with better gamut representation
pigment_names = ['Cobalt Blue', 'Hansa Yellow']
plot_color_gamut(pigment_names)

# Mix three pigments
pigment_names = ['Cobalt Blue', 'Hansa Yellow', 'Pyrrole Red']
plot_color_gamut(pigment_names)

# Mix four pigments
pigment_names = ['Cobalt Blue', 'White', 'Pyrrole Red', 'Phthalo Green']
plot_color_gamut(pigment_names)
